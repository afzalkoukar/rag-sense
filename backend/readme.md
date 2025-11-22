# DocuMind Backend API

The backend service for DocuMind, built with FastAPI and Docker. It handles PDF processing, vector embeddings, and RAG (Retrieval Augmented Generation) logic.

## 🛠️ Tech Stack

* **Framework**: FastAPI
* **Database**: PostgreSQL (Supabase) with `pgvector`
* **ORM**: SQLAlchemy (Async) + Asyncpg
* **AI**: Sentence Transformers (`all-MiniLM-L6-v2`) + Google Gemini API
* **Containerization**: Docker

## ⚙️ Setup & Installation

### 1. Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Database Connection (Use Session Mode/Port 5432 for Docker compatibility)
DATABASE_URL=postgresql+asyncpg://postgres.your-ref:[PASSWORD]@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres

# Supabase Config
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-or-service-key
SUPABASE_BUCKET=books

# Google AI
GEMINI_API_KEY=your-gemini-api-key
```

### 2. Run with Docker (Recommended)

This handles all system dependencies including PyTorch.

```bash
# Build and start
docker compose up --build

# Stop
docker compose down
```

The API will be available at: **http://localhost:8000**

### 3. API Documentation

Once running, visit the interactive Swagger UI:

👉 **http://localhost:8000/docs**

## 🧠 Key Features

* **`POST /api/upload`**: Accepts a PDF, uploads to Supabase Storage, extracts text, chunks it, generates embeddings, and saves to Postgres.
* **`GET /api/status/{id}`**: Checks if the background processing job is complete.
* **`POST /api/ask`**: Takes a query, finds the top 5 relevant chunks via Cosine Similarity, and sends them to Gemini to generate an answer.
* **`POST /api/clear/{id}`**: Deletes the file from DB and Storage (Session cleanup).

## 📂 Folder Structure

```
backend/
├── app/
│   ├── core/          # AI & PDF logic
│   ├── database.py    # Connection pool setup
│   ├── main.py        # Entry point & Routes
│   ├── models.py      # SQL Tables
│   └── schemas.py     # Pydantic Models
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```