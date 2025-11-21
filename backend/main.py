# =============================================================================
# IMPORTS SECTION
# =============================================================================

import os
import uuid
import json
import asyncio
from datetime import datetime
from typing import List, Optional

# FastAPI imports
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Pydantic
from pydantic import BaseModel

# Supabase
from supabase import create_client, Client

# SQLAlchemy
# FIX: Import NullPool is MANDATORY for Transaction Mode
from sqlalchemy.pool import NullPool 
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, Text, select, insert, update, delete, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text

# AI/ML Libraries
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# PDF Processing
import fitz 

# Environment variables
from dotenv import load_dotenv
load_dotenv()


# =============================================================================
# CONFIGURATION
# =============================================================================

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "books")
DATABASE_URL = os.getenv("DATABASE_URL")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, DATABASE_URL, GEMINI_API_KEY]):
    raise ValueError("Missing required environment variables.")


# =============================================================================
# INITIALIZE SERVICES
# =============================================================================

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("DEBUG: CONFIGURING ENGINE FOR SUPABASE TRANSACTION POOLER")

# DATABASE ENGINE FIX (Docs Approved)
# 1. NullPool: Essential for Transaction Mode (prevents connection hoarding)
# 2. statement_cache_size=0: Disables asyncpg prepared statement cache
# 3. prepared_statement_name_func: Forces SQLAlchemy to skip preparing statements
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool,
    connect_args={
        "ssl": "require",
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"stmt_{uuid.uuid4()}" # <--- THE SECRET WEAPON
    }
)

embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')


# =============================================================================
# DATABASE SCHEMA
# =============================================================================

metadata = MetaData()

books_table = Table(
    'books',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),
    Column('file_name', String(255), nullable=False),
    Column('status', String(50), nullable=False),
    Column('created_at', DateTime, nullable=False),
    Column('storage_path', String(500), nullable=True),
)

chunks_table = Table(
    'chunks',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('book_id', UUID(as_uuid=True), ForeignKey('books.id', ondelete='CASCADE'), nullable=False),
    Column('content', Text, nullable=False),
    Column('page_number', Integer, nullable=False),
    Column('chunk_index', Integer, nullable=False),
    Column('embedding', Text, nullable=True), 
    Column('created_at', DateTime, nullable=False),
)


# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class UploadResponse(BaseModel):
    upload_id: str
    file_name: str
    status: str

class StatusResponse(BaseModel):
    status: str
    file_name: str

class Citation(BaseModel):
    page: int
    snippet: str

class AskRequest(BaseModel):
    upload_id: str
    query: str

class AskResponse(BaseModel):
    answer: str
    citations: List[Citation]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)

def extract_text_from_pdf(pdf_bytes: bytes) -> dict:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = {}
    for page_num in range(len(doc)):
        pages[page_num + 1] = doc[page_num].get_text()
    doc.close()
    return pages

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    text_length = len(text)
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        if chunk.strip():
            chunks.append(chunk)
        start = end - overlap
    return chunks

async def process_book_background(upload_id: str, file_name: str, pdf_bytes: bytes):
    try:
        print(f"[{upload_id}] Extracting text from PDF...")
        # 1. Heavy Lifting (CPU) - Done in thread
        pages = await asyncio.to_thread(extract_text_from_pdf, pdf_bytes)
        
        all_chunks = []
        for page_num, page_text in pages.items():
            text_chunks = chunk_text(page_text)
            
            for chunk_idx, chunk_content in enumerate(text_chunks):
                # 2. Embeddings (Network/CPU) - Done in thread
                embedding_resp = await asyncio.to_thread(embedding_model.encode, chunk_content)
                embedding = embedding_resp.tolist()
                
                all_chunks.append({
                    'book_id': upload_id,
                    'content': chunk_content,
                    'page_number': page_num,
                    'chunk_index': chunk_idx,
                    'embedding': json.dumps(embedding),
                    'created_at': datetime.now()
                })
        
        print(f"[{upload_id}] Generated {len(all_chunks)} chunks. Saving to DB...")
        
        # FIX: Single Transaction for BOTH operations
        # This ensures we don't lose the connection between saving chunks and updating status.
        async with engine.begin() as conn:
            if all_chunks:
                await conn.execute(insert(chunks_table), all_chunks)
            
            await conn.execute(
                update(books_table)
                .where(books_table.c.id == uuid.UUID(upload_id))
                .values(status='completed')
            )
        
        print(f"[{upload_id}] Processing completed successfully")
        
    except Exception as e:
        print(f"[{upload_id}] Processing failed: {str(e)}")
        # Try to update status to failed (New transaction for error handling)
        try:
            async with engine.begin() as conn:
                await conn.execute(
                    update(books_table)
                    .where(books_table.c.id == uuid.UUID(upload_id))
                    .values(status='failed')
                )
        except Exception as db_err:
            print(f"[{upload_id}] Failed to update status to 'failed': {db_err}")


# =============================================================================
# FASTAPI APP
# =============================================================================

app = FastAPI(title="RAG-SENSE Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    print("--- [STARTUP] 1. Beginning startup sequence ---")
    try:
        print(f"--- [STARTUP] 2. Attempting to connect to DB at: {DATABASE_URL.split('@')[1]}") 
        # (This prints the host safely without password)
        
        print("--- [STARTUP] 3. Running create_tables()... (If it hangs here, network is blocked)")
        await create_tables()
        
        print("--- [STARTUP] 4. Database tables verified/created!")
    except Exception as e:
        print(f"❌ [STARTUP ERROR]: {str(e)}")
        raise e
    print("--- [STARTUP] 5. Ready to accept requests ---")


@app.get("/")
async def root():
    return {"message": "RAG-SENSE Backend is running!", "status": "healthy"}

@app.post("/api/upload", response_model=UploadResponse)
async def upload_book(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Only PDF files are allowed")
    
    upload_id = str(uuid.uuid4())
    
    try:
        pdf_bytes = await file.read()
        storage_path = f"{upload_id}/{file.filename}"
        
        try:
            supabase.storage.from_(SUPABASE_BUCKET).upload(
                path=storage_path,
                file=pdf_bytes,
                file_options={"content-type": "application/pdf"}
            )
        except Exception as e:
            print(f"Storage warning: {e}")

        async with engine.begin() as conn:
            await conn.execute(
                insert(books_table).values(
                    id=uuid.UUID(upload_id),
                    file_name=file.filename,
                    status='processing',
                    created_at=datetime.now(),
                    storage_path=storage_path
                )
            )
        
        background_tasks.add_task(process_book_background, upload_id, file.filename, pdf_bytes)
        
        return UploadResponse(upload_id=upload_id, file_name=file.filename, status="processing")
        
    except Exception as e:
        raise HTTPException(500, f"Upload failed: {str(e)}")

@app.get("/api/status/{upload_id}", response_model=StatusResponse)
async def get_status(upload_id: str):
    try:
        async with engine.connect() as conn:
            result = await conn.execute(
                select(books_table).where(books_table.c.id == uuid.UUID(upload_id))
            )
            book = result.fetchone()
        
        if not book:
            raise HTTPException(404, "Upload not found")
        
        return StatusResponse(status=book.status, file_name=book.file_name)
    except ValueError:
        raise HTTPException(400, "Invalid upload_id format")

@app.post("/api/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    try:
        print(f"[{request.upload_id}] Step 1: Finding book...")
        # 1. Check Book
        async with engine.connect() as conn:
            result = await conn.execute(
                select(books_table).where(books_table.c.id == uuid.UUID(request.upload_id))
            )
            book = result.fetchone()
        
        if not book:
            raise HTTPException(404, "Book not found")
        if book.status != 'completed':
            raise HTTPException(400, f"Book is not ready. Status: {book.status}")

        print(f"[{request.upload_id}] Step 2: Embedding query...")
        # 2. Embed Question
        query_emb_resp = await asyncio.to_thread(embedding_model.encode, request.query)
        query_embedding = query_emb_resp.tolist()
        
        print(f"[{request.upload_id}] Step 3: Fetching chunks...")
        # 3. Fetch Chunks
        async with engine.connect() as conn:
            result = await conn.execute(
                select(chunks_table).where(chunks_table.c.book_id == uuid.UUID(request.upload_id))
            )
            all_chunks = result.fetchall()
        
        if not all_chunks:
             print(f"[{request.upload_id}] Warning: No chunks found in DB!")
             raise HTTPException(500, "Document has no content.")

        print(f"[{request.upload_id}] Step 4: Calculating similarity for {len(all_chunks)} chunks...")
        # 4. Cosine Similarity
        import numpy as np
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        chunk_scores = []
        for chunk in all_chunks:
            chunk_embedding = json.loads(chunk.embedding)
            score = cosine_similarity(query_embedding, chunk_embedding)
            chunk_scores.append((score, chunk))
        
        chunk_scores.sort(reverse=True, key=lambda x: x[0])
        top_chunks = [chunk for score, chunk in chunk_scores[:5]]
        
        print(f"[{request.upload_id}] Step 5: Calling Google Gemini...")
        # 5. Ask Gemini
        context = "\n\n".join([f"[Page {c.page_number}]: {c.content}" for c in top_chunks])
        prompt = f"Answer based on this context:\n{context}\n\nQuestion: {request.query}\nAnswer:"
        
        # Print the prompt to logs to ensure it looks right
        print(f"--- PROMPT START ---\n{prompt[:200]}...\n--- PROMPT END ---")

        response = await asyncio.to_thread(gemini_model.generate_content, prompt)
        
        print(f"[{request.upload_id}] Step 6: Gemini responded!")
        
        # Check if response was blocked
        if not response.parts:
             print(f"[{request.upload_id}] Gemini blocked response: {response.prompt_feedback}")
             raise HTTPException(500, "AI declined to answer due to safety filters.")

        citations = [
            Citation(page=c.page_number, snippet=c.content[:200] + "...")
            for c in top_chunks
        ]
        
        return AskResponse(answer=response.text, citations=citations)
        
    except Exception as e:
        print(f"ERROR in ask_question: {e}")
        raise HTTPException(500, f"Error processing request: {str(e)}")

@app.post("/api/clear/{upload_id}")
async def clear_session(upload_id: str):
    try:
        target_uuid = uuid.UUID(upload_id)

        async with engine.connect() as conn:
            result = await conn.execute(
                select(books_table).where(books_table.c.id == target_uuid)
            )
            book = result.fetchone()

        if book and book.storage_path:
            try:
                supabase.storage.from_(SUPABASE_BUCKET).remove([book.storage_path])
            except:
                pass

        async with engine.begin() as conn:
            await conn.execute(
                delete(books_table).where(books_table.c.id == target_uuid)
            )
        
        return {"message": "Session cleared successfully"}
        
    except ValueError:
        raise HTTPException(400, "Invalid upload_id format")