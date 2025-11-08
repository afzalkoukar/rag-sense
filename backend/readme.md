# 1. Stop and remove the old, broken container
docker stop rag-app
docker rm rag-app

# 2. Re-build the image to include the new package
docker build -t rag-backend .

# 3. Run the new, fixed image
docker run -d --network host --env-file .env -v .:/app --name rag-app rag-backend