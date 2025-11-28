FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc g++ git curl \
    tesseract-ocr poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY ../../packages/ ./packages/

# Create logs directory
RUN mkdir -p /app/logs

# Run worker
CMD ["python", "-m", "src.worker"]
