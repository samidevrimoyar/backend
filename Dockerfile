FROM python:3.9-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Sistem bağımlılıkları
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python bağımlılıkları
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# MinIO client için gerekli
RUN pip install minio

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]