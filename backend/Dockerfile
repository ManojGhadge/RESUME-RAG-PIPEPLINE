# ---- Base image ----
FROM python:3.11-slim

WORKDIR /app

# Minimal system deps — no gcc needed (all packages have pre-built wheels)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch FIRST — prevents pip from pulling the 2GB CUDA build
# when sentence-transformers resolves its torch dependency later
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        torch==2.5.0+cpu \
        --extra-index-url https://download.pytorch.org/whl/cpu

# Install all other dependencies (sentence-transformers reuses the CPU torch above)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/uploads data/chroma

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
