import os
import uuid
import json
import asyncio
import numpy as np
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client, Client
from sqlalchemy import select, insert, update, delete

# Imports
from app.database import engine, metadata
from app.models import books_table, chunks_table
from app.schemas import (
    APIResponse,
    MessageData,
    UploadData, 
    StatusData, 
    AskData, 
    AskRequest, 
    Citation
)
from app.core.pdf import extract_text_from_pdf, chunk_text
from app.core.ai import get_embedding, generate_answer

# Config
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "books")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(title="RAG-SENSE Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper: Now defaults to "Success" instead of None
def create_response(data=None, message="Success", status_code=200):
    return APIResponse(
        status_code=status_code,
        timestamp=datetime.now().isoformat(),
        data=data,
        message=message
    )

@app.on_event("startup")
async def startup_event():
    print("🚀 Starting RAG-SENSE Backend...")
    async with engine.begin() as conn:
        await conn.run_sync(metadata.create_all)
    print("✅ Database Ready.")

@app.get("/", response_model=APIResponse[MessageData])
def root():
    return create_response(
        data=MessageData(message="RAG-SENSE Backend is running!"),
        message="Health check passed"
    )

# --- Background Worker ---
async def process_book_background(upload_id: str, file_name: str, pdf_bytes: bytes):
    try:
        print(f"[{upload_id}] Processing started...")
        pages = await asyncio.to_thread(extract_text_from_pdf, pdf_bytes)
        
        all_chunks = []
        for page_num, page_text in pages.items():
            text_chunks = chunk_text(page_text)
            for idx, content in enumerate(text_chunks):
                emb = await asyncio.to_thread(get_embedding, content)
                all_chunks.append({
                    'book_id': upload_id,
                    'content': content,
                    'page_number': page_num,
                    'chunk_index': idx,
                    'embedding': json.dumps(emb),
                    'created_at': datetime.now()
                })
        
        async with engine.begin() as conn:
            if all_chunks:
                await conn.execute(insert(chunks_table), all_chunks)
            await conn.execute(
                update(books_table)
                .where(books_table.c.id == uuid.UUID(upload_id))
                .values(status='completed')
            )
        print(f"[{upload_id}] Completed.")
    except Exception as e:
        print(f"[{upload_id}] FAILED: {e}")
        try:
            async with engine.begin() as conn:
                await conn.execute(update(books_table).where(books_table.c.id == uuid.UUID(upload_id)).values(status='failed'))
        except:
            pass

# --- Routes ---

@app.post("/api/upload", response_model=APIResponse[UploadData])
async def upload_book(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(400, "PDFs only")
    
    upload_id = str(uuid.uuid4())
    
    try:
        pdf_bytes = await file.read()
        try:
            supabase.storage.from_(SUPABASE_BUCKET).upload(f"{upload_id}/{file.filename}", pdf_bytes, file_options={"content-type": "application/pdf"})
        except Exception:
            pass

        async with engine.begin() as conn:
            await conn.execute(insert(books_table).values(
                id=uuid.UUID(upload_id),
                file_name=file.filename,
                status='processing',
                created_at=datetime.now(),
                storage_path=f"{upload_id}/{file.filename}"
            ))
        
        background_tasks.add_task(process_book_background, upload_id, file.filename, pdf_bytes)
        
        return create_response(
            data=UploadData(
                upload_id=upload_id, 
                file_name=file.filename, 
                status="processing"
            ),
            message="File uploaded successfully"
        )
        
    except Exception as e:
        raise HTTPException(500, f"Upload error: {e}")

@app.get("/api/status/{upload_id}", response_model=APIResponse[StatusData])
async def get_status(upload_id: str):
    async with engine.connect() as conn:
        res = await conn.execute(select(books_table).where(books_table.c.id == uuid.UUID(upload_id)))
        book = res.fetchone()
    
    if not book: raise HTTPException(404, "Not found")
    
    return create_response(
        data=StatusData(
            status=book.status, 
            file_name=book.file_name
        ),
        message="Status retrieved"
    )

@app.post("/api/ask", response_model=APIResponse[AskData])
async def ask_question(request: AskRequest):
    async with engine.connect() as conn:
        res = await conn.execute(select(books_table).where(books_table.c.id == uuid.UUID(request.upload_id)))
        book = res.fetchone()
    
    if not book: raise HTTPException(404, "Not found")
    if book.status != 'completed': raise HTTPException(400, "Book processing not complete")

    q_emb = await asyncio.to_thread(get_embedding, request.query)

    async with engine.connect() as conn:
        res = await conn.execute(select(chunks_table).where(chunks_table.c.book_id == uuid.UUID(request.upload_id)))
        db_chunks = res.fetchall()

    if not db_chunks: raise HTTPException(500, "No content found in document")

    scores = []
    for chunk in db_chunks:
        v = json.loads(chunk.embedding)
        score = np.dot(q_emb, v) / (np.linalg.norm(q_emb) * np.linalg.norm(v))
        scores.append((score, chunk))
    
    scores.sort(reverse=True, key=lambda x: x[0])
    top_k = scores[:5]

    context = "\n".join([f"[Page {c.page_number}] {c.content}" for _, c in top_k])
    prompt = f"Context:\n{context}\n\nQuestion: {request.query}\nAnswer:"
    
    resp = await asyncio.to_thread(generate_answer, prompt)
    
    return create_response(
        data=AskData(
            answer=resp.text,
            citations=[Citation(page=c.page_number, snippet=c.content[:150]+"...") for _, c in top_k]
        ),
        message="Answer generated successfully"
    )

@app.post("/api/clear/{upload_id}", response_model=APIResponse[MessageData])
async def clear_session(upload_id: str):
    try:
        target_uuid = uuid.UUID(upload_id)
        
        async with engine.connect() as conn:
            res = await conn.execute(select(books_table).where(books_table.c.id == target_uuid))
            book = res.fetchone()

        if book and book.storage_path:
            try:
                supabase.storage.from_(SUPABASE_BUCKET).remove([book.storage_path])
            except:
                pass

        async with engine.begin() as conn:
            await conn.execute(delete(books_table).where(books_table.c.id == target_uuid))
            
        return create_response(
            data=MessageData(message="File and data deleted"),
            message="Session cleared successfully"
        )
    except ValueError:
        raise HTTPException(400, "Invalid ID")