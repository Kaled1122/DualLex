FROM python:3.10-slim

# Install system deps for Playwright
RUN apt-get update && apt-get install -y \
    wget gnupg ca-certificates \
    libnss3 libxkbcommon0 libatk-bridge2.0-0 libfontconfig1 libgtk-3-0 \
    libdrm2 libgbm1 libxshmfence1 libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Install Python libs
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright + Chromium
RUN playwright install chromium

COPY . .

# Start server
CMD ["python", "app.py"]
