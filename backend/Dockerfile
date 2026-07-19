# ---- Base image ----
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps needed by PyMuPDF and cryptography
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python deps first (layer cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data dirs
RUN mkdir -p data/uploads data/chroma

# Expose port
EXPOSE 8000

# Uvicorn — no --reload in production
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
