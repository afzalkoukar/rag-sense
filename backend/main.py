import os
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List, Optional

# --- Pydantic Models (The API "Contract") ---

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

# --- Create FastAPI App ---
app = FastAPI()

# --- API Endpoints (The "Skeleton") ---

@app.get("/")
async def root():
    """A simple root endpoint to check if the server is running."""
    return {"message": "BookQ Backend is running!"}

@app.post("/api/upload", response_model=UploadResponse)
async def upload_book(file: UploadFile = File(...)):
    # 1. TODO: Upload file to Supabase Storage
    # 2. TODO: Create 'book' record in Supabase Postgres
    # 3. TODO: Start background task to process the book
    # 4. TODO: Return 'upload_id' immediately
    return {"upload_id": "mock-id", "file_name": file.filename, "status": "processing"}

@app.get("/api/status/{upload_id}", response_model=StatusResponse)
async def get_status(upload_id: str):
    # 1. TODO: Query 'books' table in Postgres
    # 2. TODO: Return the status
    return {"status": "mock-status", "file_name": "mock-file.pdf"}

@app.post("/api/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    # 1. TODO: Embed the 'request.query' using MiniLM
    # 2. TODO: Search 'chunks' table in pgvector for matches
    # 3. TODO: Build prompt with retrieved chunks
    # 4. TODO: Call Google Gemini API
    # 5. TODO: Post-check and format the response
    return {
        "answer": "This is a mock answer from the book.",
        "citations": [
            {"page": 42, "snippet": "...a mock snippet from page 42..."}
        ]
    }

@app.post("/api/clear/{upload_id}")
async def clear_session(upload_id: str):
    # 1. TODO: Delete file from Supabase Storage
    # 2. TODO: Delete 'book' record (and all 'chunks' via CASCADE)
    return {"message": "Session cleared successfully."}