# bench-app/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# copy pip requirements & install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy your bench script
COPY bench_docker.py .

# default command is overridden by compose
CMD ["python", "bench_docker.py"]
