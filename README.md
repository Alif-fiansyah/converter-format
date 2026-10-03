# Telegram Document Converter Bot

A robust, production-ready Telegram bot built with `python-telegram-bot` and `LibreOffice` that seamlessly converts various office and document formats into PDFs, and vice versa. Fully containerized with Docker and ready for 24/7 cloud deployment.

---

## Features

- **Office ➡️ PDF Conversion:** Supports `docx`, `doc`, `odt`, `rtf`, `txt`, `xlsx`, `xls`, `csv`, `ods`, `pptx`, `ppt`, and `odp`.
- **PDF ➡️ Office Conversion:** Converts PDF files back into editable formats (`docx`, `xlsx`, `pptx`) using `pdf2docx` and LibreOffice headless mode.
- **Production-Ready Security & Stability:**
  - File size validation (default max 20 MB limit to prevent server overload).
  - Robust error handling and fallback logic.
  - Automated secure cleanup (`finally` block) to remove local temp files and prevent storage buildup.
- **Interactive Menu:** Clean inline keyboard interface for effortless user navigation.

---

## Tech Stack

- **Python 3.10+**
- **python-telegram-bot**
- **pdf2docx**
- **LibreOffice (Headless Mode)**
- **Docker**

---

## Local Installation & Setup

If you want to run or test the bot locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Alif-fiansyah/converter-format.git
   cd converter-format
   ```

2. **Install system dependencies (LibreOffice):**
   * *Ubuntu / Debian:*
     ```bash
     sudo apt update && sudo apt install libreoffice -y
     ```

3. **Set up a Python virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your bot token:
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

5. **Run the bot:**
   ```bash
   python bot.py
   ```

---

## 🐳 Docker Deployment

This project includes a `Dockerfile` for seamless deployment to cloud platforms (like Railway, Render, or a custom VPS):

```dockerfile
FROM python:3.10-slim

# Install LibreOffice and dependencies
RUN apt-get update && apt-get install -y \
    libreoffice \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

---

## 👤 Author

* **Lifianzhi**
* GitHub: [@Alif-fiansyah](https://github.com/Alif-fiansyah)
