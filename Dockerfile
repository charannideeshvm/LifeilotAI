# LifePilot AI — Dockerfile for Google Cloud Run

# Official Python slim image — small and secure
FROM python:3.11-slim

# Prevents Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Prevents Python from buffering stdout/stderr
# This ensures logs appear immediately in Cloud Run
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies first
# Docker caches this layer — reinstall only when requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY backend/ ./backend/

# Move into backend directory
WORKDIR /app/backend

# Cloud Run sets PORT environment variable automatically
# Default to 8080 if not set
ENV PORT=8080

# Expose the port
EXPOSE 8080

# Start command
CMD uvicorn main:app --host 0.0.0.0 --port $PORT