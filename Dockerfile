# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies for audio/video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Ensure necessary directories exist
RUN mkdir -p /app/dataset /app/chroma_db /app/uploads

# Set environment variables
ENV OLLAMA_HOST=http://ollama:11434
ENV PORT=8000
ENV PYTHONUNBUFFERED=1

# Run the API server
CMD ["python", "auralis_api.py"]
