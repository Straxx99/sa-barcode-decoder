FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Copy application files
COPY app_sa.py .
COPY sa_license_decoder.py .

# Expose port
EXPOSE 5000

# Run with gunicorn (use PORT env var for Railway)
CMD gunicorn --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120 app_sa:app
