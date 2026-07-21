# ---- Base image ----
FROM python:3.11-slim

WORKDIR /app

# System deps needed by PyMuPDF and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch FIRST — prevents pip from pulling the 2GB CUDA build
# when sentence-transformers resolves its torch dependency later
RUN pip install --no-cache-dir \
    torch==2.2.2+cpu \
    --extra-index-url https://download.pytorch.org/whl/cpu

# Now install everything else (sentence-transformers will reuse the CPU torch above)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data/uploads data/chroma

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
