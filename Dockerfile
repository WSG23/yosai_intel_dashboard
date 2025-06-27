FROM python:3.11-slim AS base

# Builder stage
FROM base AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# Production image
FROM base
WORKDIR /app
COPY --from=builder /install /usr/local
COPY . .

EXPOSE 8050

HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8050/ || exit 1

CMD ["python", "app.py"]
