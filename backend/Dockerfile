# ---- Base image ----
FROM python:3.11-slim

WORKDIR /app

# Install only minimal system deps
# cryptography now ships pre-built wheels so gcc is NOT needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch FIRST to avoid pulling the 2GB CUDA build
RUN pip install --no-cache-dir \
    torch==2.2.2+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Install all other dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/uploads data/chroma

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
