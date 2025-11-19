# =============================================================================
# IMPORTS SECTION
# =============================================================================

import os
import uuid
from datetime import datetime
from typing import List, Optional

# FastAPI imports - Web framework for building APIs
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Pydantic - Data validation and serialization
from pydantic import BaseModel

# Supabase - Cloud database and storage
from supabase import create_client, Client

# SQLAlchemy - Database ORM for async operations
print("DEBUG: IMPORTING SQLALCHEMY WITH POOL NULLPOOL")
from sqlalchemy.pool import NullPool
from sqlalchemy import Table, Column, Integer, String, DateTime, MetaData, Text, select, insert, update, delete, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text

# AI/ML Libraries
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# PDF Processing
import fitz  # PyMuPDF for extracting text from PDFs

# Environment variables
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# =============================================================================
# ENVIRONMENT VARIABLES & CONFIGURATION
# =============================================================================

# Supabase credentials for storage (file uploads)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "books")

# Database connection string for PostgreSQL with pgvector
DATABASE_URL = os.getenv("DATABASE_URL")

# Google Gemini API key for generating answers
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Validate all required environment variables are present
if not all([SUPABASE_URL, SUPABASE_KEY, DATABASE_URL, GEMINI_API_KEY]):
    raise ValueError("Missing required environment variables. Check your .env file.")


# =============================================================================
# INITIALIZE SERVICES
# =============================================================================

# Initialize Supabase client for file storage operations
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

print("DEBUG: CONFIGURING DATABASE ENGINE WITH CACHE=0")

# Initialize async database engine for PostgreSQL operations
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,
    poolclass=NullPool,  # <--- THIS IS THE KEY FIX
    connect_args={
        "ssl": "require",
        "statement_cache_size": 0
    }
)

# Initialize embedding model for converting text to vectors
# MiniLM is a small, fast model that creates 384-dimensional embeddings
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Configure Google Gemini AI for generating answers
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')


# =============================================================================
# DATABASE SCHEMA DEFINITION
# =============================================================================

# MetaData object holds all table definitions
metadata = MetaData()

# BOOKS TABLE - Stores information about uploaded PDFs
books_table = Table(
    'books',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True),  # Unique identifier
    Column('file_name', String(255), nullable=False),     # Original PDF filename
    Column('status', String(50), nullable=False),         # processing/completed/failed
    Column('created_at', DateTime, nullable=False),       # Upload timestamp
    Column('storage_path', String(500), nullable=True),   # Path in Supabase Storage
)

# CHUNKS TABLE - Stores text segments with embeddings from PDFs
# Each chunk is a paragraph or section with its vector embedding
chunks_table = Table(
    'chunks',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('book_id', UUID(as_uuid=True), ForeignKey('books.id', ondelete='CASCADE'), nullable=False),
    Column('content', Text, nullable=False),              # The actual text content
    Column('page_number', Integer, nullable=False),       # Which page this came from
    Column('chunk_index', Integer, nullable=False),       # Order within the page
    Column('embedding', Text, nullable=True),             # Vector embedding as text (will use pgvector in production)
    Column('created_at', DateTime, nullable=False),
)


# =============================================================================
# PYDANTIC MODELS (API DATA CONTRACTS)
# =============================================================================

class UploadResponse(BaseModel):
    """
    Response returned after uploading a PDF.
    Client uses upload_id to check status and ask questions.
    """
    upload_id: str
    file_name: str
    status: str


class StatusResponse(BaseModel):
    """
    Response for checking processing status of an uploaded book.
    """
    status: str      # "processing", "completed", or "failed"
    file_name: str


class Citation(BaseModel):
    """
    A single citation showing where information came from in the book.
    """
    page: int        # Page number
    snippet: str     # Text excerpt from that page


class AskRequest(BaseModel):
    """
    Request body for asking a question about a book.
    """
    upload_id: str   # Which book to query
    query: str       # The question to answer


class AskResponse(BaseModel):
    """
    Response containing AI-generated answer with source citations.
    """
    answer: str
    citations: List[Citation]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def create_tables():
    """
    Create database tables if they don't exist.
    Called on application startup.
    """
    async with engine.begin() as conn:
        # Create tables (will skip if they already exist)
        await conn.run_sync(metadata.create_all)


def extract_text_from_pdf(pdf_bytes: bytes) -> dict:
    """
    Extract text from PDF file, organized by pages.
    
    Args:
        pdf_bytes: Raw PDF file content as bytes
        
    Returns:
        Dictionary mapping page numbers to text content
        Example: {1: "Chapter 1 text...", 2: "Chapter 2 text..."}
    """
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages = {}
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        pages[page_num + 1] = text  # Page numbers start at 1, not 0
    
    doc.close()
    return pages


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into smaller chunks for embedding.
    Uses overlapping chunks to maintain context across boundaries.
    
    Args:
        text: The text to split
        chunk_size: Target size of each chunk in characters
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
        
    Example:
        If text is "ABCDEFGHIJ" with chunk_size=4 and overlap=1:
        Returns: ["ABCD", "DEFG", "GHIJ"]
    """
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        # Extract chunk from start to start+chunk_size
        end = start + chunk_size
        chunk = text[start:end]
        
        if chunk.strip():  # Only add non-empty chunks
            chunks.append(chunk)
        
        # Move start forward, with overlap
        start = end - overlap
    
    return chunks


async def process_book_background(upload_id: str, file_name: str, pdf_bytes: bytes):
    """
    Background task that processes a PDF after upload.
    This runs asynchronously so the upload endpoint can return immediately.
    
    Steps:
        1. Extract text from all pages
        2. Split text into chunks
        3. Generate embeddings for each chunk
        4. Store chunks in database
        5. Update book status to 'completed' or 'failed'
        
    Args:
        upload_id: Unique identifier for this book
        file_name: Original filename
        pdf_bytes: Raw PDF content
    """
    try:
        # Step 1: Extract text from PDF pages
        print(f"[{upload_id}] Extracting text from PDF...")
        pages = extract_text_from_pdf(pdf_bytes)
        
        # Step 2: Process each page
        all_chunks = []
        for page_num, page_text in pages.items():
            # Split page text into chunks
            text_chunks = chunk_text(page_text)
            
            # Create chunk records with metadata
            for chunk_idx, chunk_content in enumerate(text_chunks):
                # Generate embedding for this chunk
                embedding = embedding_model.encode(chunk_content).tolist()
                
                all_chunks.append({
                    'book_id': upload_id,
                    'content': chunk_content,
                    'page_number': page_num,
                    'chunk_index': chunk_idx,
                    'embedding': str(embedding),  # Store as string for now
                    'created_at': datetime.now()
                })
        
        print(f"[{upload_id}] Generated {len(all_chunks)} chunks")
        
        # Step 3: Insert all chunks into database
        async with engine.begin() as conn:
            if all_chunks:
                await conn.execute(insert(chunks_table), all_chunks)
        
        # Step 4: Update book status to completed
        async with engine.begin() as conn:
            await conn.execute(
                update(books_table)
                .where(books_table.c.id == uuid.UUID(upload_id))
                .values(status='completed')
            )
        
        print(f"[{upload_id}] Processing completed successfully")
        
    except Exception as e:
        # If anything fails, mark the book as failed
        print(f"[{upload_id}] Processing failed: {str(e)}")
        
        async with engine.begin() as conn:
            await conn.execute(
                update(books_table)
                .where(books_table.c.id == uuid.UUID(upload_id))
                .values(status='failed')
            )


# =============================================================================
# CREATE FASTAPI APPLICATION
# =============================================================================

app = FastAPI(
    title="RAG-SENSE Backend",
    description="Question-answering system for PDF books using RAG",
    version="1.0.0"
)

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# STARTUP EVENT
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """
    Called when the server starts.
    Ensures database tables exist.
    """
    print("Starting up RAG-SENSE backend...")
    await create_tables()
    print("Database tables ready")


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.get("/")
async def root():
    """
    Health check endpoint.
    
    Returns:
        Simple message confirming server is running
        
    Example:
        GET http://localhost:8000/
        Response: {"message": "RAG-SENSE Backend is running!"}
    """
    return {
        "message": "RAG-SENSE Backend is running with docker compose!",
        "version": "1.0.0",
        "status": "healthy"
    }


@app.post("/api/upload", response_model=UploadResponse)
async def upload_book(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...)
):
    """
    Upload a PDF book for processing.
    
    Process:
        1. Validate file is a PDF
        2. Generate unique upload ID
        3. Upload file to Supabase Storage
        4. Create book record in database
        5. Start background processing
        6. Return immediately with upload_id
        
    Args:
        background_tasks: FastAPI's background task manager
        file: The uploaded PDF file
        
    Returns:
        UploadResponse with upload_id and status
        
    Raises:
        HTTPException 400: If file is not a PDF
        HTTPException 500: If upload fails
    """
    
    # Step 1: Validate file type
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed"
        )
    
    # Step 2: Generate unique upload ID
    upload_id = str(uuid.uuid4())
    
    try:
        # Step 3: Read file content
        pdf_bytes = await file.read()
        
        # Step 4: Upload to Supabase Storage
        storage_path = f"{upload_id}/{file.filename}"
        supabase.storage.from_(SUPABASE_BUCKET).upload(
            path=storage_path,
            file=pdf_bytes,
            file_options={"content-type": "application/pdf"}
        )
        
        # Step 5: Create book record in database
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
        
        # Step 6: Start background processing
        # This runs asynchronously - we return immediately
        background_tasks.add_task(
            process_book_background,
            upload_id,
            file.filename,
            pdf_bytes
        )
        
        return UploadResponse(
            upload_id=upload_id,
            file_name=file.filename,
            status="processing"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Upload failed: {str(e)}"
        )


@app.get("/api/status/{upload_id}", response_model=StatusResponse)
async def get_status(upload_id: str):
    """
    Check processing status of an uploaded book.
    
    Args:
        upload_id: The unique ID from upload response
        
    Returns:
        StatusResponse with current status
        
    Raises:
        HTTPException 404: If upload_id not found
    """
    
    try:
        # Query database for this book
        async with engine.connect() as conn:
            result = await conn.execute(
                select(books_table).where(
                    books_table.c.id == uuid.UUID(upload_id)
                )
            )
            book = result.fetchone()
        
        # Check if book exists
        if not book:
            raise HTTPException(
                status_code=404,
                detail="Upload not found"
            )
        
        return StatusResponse(
            status=book.status,
            file_name=book.file_name
        )
        
    except ValueError:
        # Invalid UUID format
        raise HTTPException(
            status_code=400,
            detail="Invalid upload_id format"
        )


@app.post("/api/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Ask a question about an uploaded book using RAG.
    
    RAG Process (Retrieval-Augmented Generation):
        1. Convert question to embedding vector
        2. Search for similar chunks in database (retrieval)
        3. Build context from relevant chunks (augmentation)
        4. Send context + question to AI (generation)
        5. Return answer with citations
        
    Args:
        request: AskRequest with upload_id and query
        
    Returns:
        AskResponse with answer and citations
        
    Raises:
        HTTPException 404: If book not found
        HTTPException 400: If book not ready
    """
    
    try:
        # Step 1: Verify book exists and is ready
        async with engine.connect() as conn:
            result = await conn.execute(
                select(books_table).where(
                    books_table.c.id == uuid.UUID(request.upload_id)
                )
            )
            book = result.fetchone()
        
        if not book:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )
        
        if book.status != 'completed':
            raise HTTPException(
                status_code=400,
                detail=f"Book is not ready. Current status: {book.status}"
            )
        
        # Step 2: Generate embedding for the query
        query_embedding = embedding_model.encode(request.query).tolist()
        
        # Step 3: Find similar chunks
        # Note: This is a simplified version. In production, use pgvector's
        # cosine similarity function for better performance
        async with engine.connect() as conn:
            result = await conn.execute(
                select(chunks_table).where(
                    chunks_table.c.book_id == uuid.UUID(request.upload_id)
                )
            )
            all_chunks = result.fetchall()
        
        # Calculate similarity scores (simplified)
        # In production, use pgvector's <=> operator
        import numpy as np
        
        def cosine_similarity(a, b):
            return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
        
        chunk_scores = []
        for chunk in all_chunks:
            chunk_embedding = eval(chunk.embedding)  # Convert string back to list
            score = cosine_similarity(query_embedding, chunk_embedding)
            chunk_scores.append((score, chunk))
        
        # Sort by similarity and take top 5
        chunk_scores.sort(reverse=True, key=lambda x: x[0])
        top_chunks = [chunk for score, chunk in chunk_scores[:5]]
        
        # Step 4: Build context from relevant chunks
        context = "\n\n".join([
            f"[Page {chunk.page_number}]: {chunk.content}"
            for chunk in top_chunks
        ])
        
        # Step 5: Build prompt for Gemini
        prompt = f"""You are a helpful assistant answering questions about a book.
Use ONLY the following excerpts from the book to answer the question.
If the answer is not in the excerpts, say "I cannot find this information in the provided text."
Be concise and accurate.

Book excerpts:
{context}

Question: {request.query}

Answer:"""
        
        # Step 6: Call Gemini API
        response = gemini_model.generate_content(prompt)
        answer = response.text
        
        # Step 7: Build citations
        citations = [
            Citation(
                page=chunk.page_number,
                snippet=chunk.content[:200] + ("..." if len(chunk.content) > 200 else "")
            )
            for chunk in top_chunks
        ]
        
        return AskResponse(
            answer=answer,
            citations=citations
        )
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid upload_id format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process question: {str(e)}"
        )


@app.post("/api/clear/{upload_id}")
async def clear_session(upload_id: str):
    """
    Delete a book and all its data.
    
    Process:
        1. Delete file from Supabase Storage
        2. Delete book record (CASCADE deletes chunks)
        
    Args:
        upload_id: The book to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException 404: If book not found
    """
    
    try:
        # Step 1: Get book info (to find storage path)
        async with engine.connect() as conn:
            result = await conn.execute(
                select(books_table).where(
                    books_table.c.id == uuid.UUID(upload_id)
                )
            )
            book = result.fetchone()
        
        if not book:
            raise HTTPException(
                status_code=404,
                detail="Book not found"
            )
        
        # Step 2: Delete from Supabase Storage
        try:
            if book.storage_path:
                supabase.storage.from_(SUPABASE_BUCKET).remove([book.storage_path])
        except Exception as e:
            # File might already be deleted, continue anyway
            print(f"Storage deletion warning: {str(e)}")
        
        # Step 3: Delete book record (CASCADE deletes all chunks)
        async with engine.begin() as conn:
            await conn.execute(
                delete(books_table).where(
                    books_table.c.id == uuid.UUID(upload_id)
                )
            )
        
        return {"message": "Session cleared successfully"}
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid upload_id format"
        )


# =============================================================================
# HOW TO RUN THIS APPLICATION
# =============================================================================
#
# 1. Make sure all environment variables are set in .env:
#    - SUPABASE_URL
#    - SUPABASE_KEY
#    - SUPABASE_BUCKET
#    - DATABASE_URL
#    - GEMINI_API_KEY
#
# 2. Install dependencies:
#    pip install -r requirements.txt
#
# 3. Run with Docker:
#    docker build -t rag-backend .
#    docker run -d --network host --env-file .env -v .:/app --name rag-app rag-backend
#
# 4. Test the API:
#    curl http://localhost:8000/
#
# 5. Access interactive docs:
#    http://localhost:8000/docs
#
# =============================================================================