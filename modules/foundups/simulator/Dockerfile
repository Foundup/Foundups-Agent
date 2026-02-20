# SSE Server for FoundUps Cube Events
# Deploy to Cloud Run: gcloud run deploy sse-foundups --source .

FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-sse.txt .
RUN pip install --no-cache-dir -r requirements-sse.txt

# Copy application code
COPY sse_server.py .

# Cloud Run uses PORT env var
ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Run with simulate mode by default (FAMDaemon not available in Cloud Run)
CMD ["python", "sse_server.py", "--simulate"]
