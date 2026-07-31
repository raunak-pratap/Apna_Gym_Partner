FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies required for media, WebRTC, OpenCV and building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    ffmpeg \
    pkg-config \
    libssl-dev \
    libffi-dev \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Copy the app's requirements (use the file inside Main_App)
COPY Main_App/requirements.txt /app/requirements.txt

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the repo
COPY . /app

# (Optional) Expose the traditional Streamlit port for local runs
EXPOSE 8501

# Healthcheck uses the runtime PORT env var set by Railway (shell form expands $PORT)
HEALTHCHECK CMD curl --fail http://localhost:$PORT/_stcore/health || exit 1

# Run Streamlit on the PORT Railway provides and bind to all interfaces
CMD ["sh", "-c", "streamlit run Main_App/main.py --server.address=0.0.0.0 --server.port=${PORT:-8501} --server.enableCORS false"]
