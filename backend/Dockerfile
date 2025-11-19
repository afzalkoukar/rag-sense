# 1. Use official Python base
FROM python:3.11-slim

# 2. Set working directory
WORKDIR /app

# 3. Copy requirements first (better caching)
COPY requirements.txt .

# 4. Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of the code
COPY . .

# 6. (Optional) Documentation that the app listens on 8000
EXPOSE 8000

# 7. Run the app with --reload enabled for live updates
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]