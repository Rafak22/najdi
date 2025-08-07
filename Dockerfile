FROM python:3.11-slim

# Install ffmpeg for audio processing
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Only install needed dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only necessary files
COPY . .

# Run the application
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port=${PORT:-8000}"]