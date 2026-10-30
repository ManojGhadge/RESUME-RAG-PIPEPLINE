# ---- Base image ----
FROM python:3.11-slim

WORKDIR /app

# Minimal system deps — no gcc needed (all packages have pre-built wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install all Python dependencies
# sentence-transformers will pull torch CPU automatically via its dependencies
# We don't pre-install torch separately to avoid hash/CDN issues
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/uploads data/chroma

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
