FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_APP=task3.py \
    FLASK_ENV=production \
    PORT=8000

# Install system dependencies (required for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only necessary files (improves build caching)
COPY requirements.txt .
COPY task3.py .
COPY config/ ./config/ 
COPY .env .             

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Expose the port the app runs on
EXPOSE $PORT

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "task3:app"]