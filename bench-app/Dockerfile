# bench-app/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy load‑test script
COPY load_test.py .

# Default command overridden by docker-compose.yml
CMD ["python", "load_test.py"]
