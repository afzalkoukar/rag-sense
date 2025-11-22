import os
import google.generativeai as genai
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not set")

# Initialize Models
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash') 

def get_embedding(text: str):
    return embedding_model.encode(text).tolist()

def generate_answer(prompt: str):
    return gemini_model.generate_content(prompt)