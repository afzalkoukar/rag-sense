# 1. Use an official Python base image
FROM python:3.11-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy just the requirements file first
COPY requirements.txt .

# 4. Install the Python dependencies
# Using --no-cache-dir makes the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy the rest of your application code
COPY . .

# 6. Expose the port that FastAPI will run on (default is 8000)
EXPOSE 8000

# 7. The command to run your application
# This runs: uvicorn main:app --host 0.0.0.0 --port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]