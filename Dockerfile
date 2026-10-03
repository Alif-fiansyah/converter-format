# Gunakan image dasar Python
FROM python:3.11-slim

# Install LibreOffice dan dependensi sistem untuk konversi dokumen
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    && rm -rf /var/lib/apt/lists/*

# Set working directory di dalam container
WORKDIR /app

# Salin dan install dependencies Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Salin seluruh kode bot ke container
COPY . .

# Jalankan bot
CMD ["python", "bot.py"]