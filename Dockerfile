FROM python:3.10-slim

# Set a working directory
WORKDIR /app

# Install build deps for scikit-learn (kept minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
  && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy app
COPY . /app

EXPOSE 5000

# Use a non-root user in production (optional step omitted for brevity)
CMD ["python", "app.py"]
