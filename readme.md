# DocuMind: Intelligent Document Chat

DocuMind is a full-stack RAG (Retrieval Augmented Generation) application that allows users to upload PDF documents and chat with them using AI. It transforms static documents into interactive conversations.

## 🚀 Features

* 📄 **PDF Ingestion**: Upload resumes, books, or reports.
* 🧠 **Smart Embeddings**: Automatically chunks and vectorizes text using `sentence-transformers`.
* 💬 **AI Chat**: Ask questions and get accurate answers powered by Google Gemini 2.5 Flash.
* 📚 **Citations**: Every answer includes page numbers and text snippets from the source.
* ⚡ **Real-time**: Non-blocking upload process with live status updates.

## 🏗️ Architecture

* **Frontend**: Next.js 14 (App Router), Tailwind CSS, TypeScript.
* **Backend**: FastAPI (Python), Docker, SQLAlchemy (Async).
* **Database**: Supabase (PostgreSQL + pgvector).
* **AI Models**:
   * Embeddings: `all-MiniLM-L6-v2` (Local/HuggingFace).
   * LLM: Google Gemini 2.5 Flash via API.

## 📂 Project Structure

This repository is a monorepo containing both the frontend and backend services.

| Service | Path | Description |
|---------|------|-------------|
| Frontend | `/frontend` | Next.js application for the user interface. |
| Backend | `/backend` | FastAPI server handling storage, embeddings, and RAG logic. |

## 🏁 Quick Start

You need to run both services to use the application fully.

### 1. Start Backend

```bash
cd backend
# Copy .env.example to .env and add your API keys
docker compose up --build
```

Backend runs on: `http://localhost:8000`

### 2. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on: `http://localhost:3000`

## 🛠️ Requirements

* Docker & Docker Compose
* Node.js 18+
* A Supabase Project (Free Tier)
* Google Gemini API Key

## 📄 License

MIT