# 🧠 Rag Sense

**Rag Sense** is an intelligent RAG (Retrieval-Augmented Generation) framework designed to help developers quickly build, test, and deploy AI-powered retrieval systems. It provides modular components for document ingestion, embedding, retrieval, and LLM-based reasoning.

---

## 🚀 Features

- 🔍 Document ingestion and vectorization
- 🧩 Plug-and-play retriever architecture
- 🗂️ Support for multiple data sources (PDFs, text, CSVs, etc.)
- ⚙️ Configurable pipeline with minimal setup
- 🧠 LLM response orchestration
- 🧾 Extensible backend ready for experimentation

---

## 🛠️ Tech Stack

- **Python 3.10+**
- **LangChain / LlamaIndex**
- **FAISS / Chroma** for vector storage
- **OpenAI / HuggingFace** for LLM integration
- **FastAPI** 

---

## ⚙️ Installation

Clone the repository and install dependencies:

```bash
git clone git@github.com:afzalkoukar/rag-sense.git
cd rag-sense
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt