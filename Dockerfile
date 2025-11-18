FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

# Install system libs + Chromium
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget gnupg ca-certificates \
    libnss3 libatk-bridge2.0-0 libgtk-3-0 \
    libxkbcommon0 libfontconfig1 libasound2 libpangocairo-1.0-0 \
    libdrm2 libgbm1 libxshmfence1 \
    chromium \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright + Chromium driver
RUN playwright install chromium

COPY . .

CMD ["python", "app.py"]
