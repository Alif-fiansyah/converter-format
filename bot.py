import os
import subprocess
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Batas maksimal ukuran file (contoh: 20 MB dalam bytes)
MAX_FILE_SIZE = 20 * 1024 * 1024 

# Menu utama /start
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 **Hai, Selamat datang di Converter Format Bot!**\n\n"
        "Pilih jenis konversi yang kamu inginkan atau langsung kirim file dokumenmu ke sini:\n\n"
        "⚠️ *Catatan: Maksimal ukuran file adalah 20 MB.*"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📄 Office ➡️ PDF", callback_data="menu_to_pdf")
        ],
        [
            InlineKeyboardButton("📝 PDF ➡️ Word", callback_data="pdf_to_docx"),
            InlineKeyboardButton("📊 PDF ➡️ Excel", callback_data="pdf_to_xlsx")
        ],
        [
            InlineKeyboardButton("📈 PDF ➡️ PPT", callback_data="pdf_to_pptx")
        ],
        [
            InlineKeyboardButton("🌐 GitHub", url="https://github.com/Alif-fiansyah")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(welcome_text, parse_mode="Markdown", reply_markup=reply_markup)

# Handler pilihan tombol interaktif
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "menu_to_pdf":
        text = "📄 **Mode: Ke PDF aktif.**\nSilakan kirim file Word, Excel, PPT, atau TXT ke sini!"
    elif query.data == "pdf_to_docx":
        text = "📝 **Mode: PDF ke Word (DOCX) aktif.**\nSilakan kirim file PDF kamu ke sini!"
    elif query.data == "pdf_to_xlsx":
        text = "📊 **Mode: PDF ke Excel (XLSX) aktif.**\nSilakan kirim file PDF tabel kamu ke sini!"
    elif query.data == "pdf_to_pptx":
        text = "📈 **Mode: PDF ke PowerPoint (PPTX) aktif.**\nSilakan kirim file PDF presentasi kamu ke sini!"
    else:
        text = "Silakan kirim dokumen yang ingin kamu konversi."

    await query.message.edit_text(text, parse_mode="Markdown")

# Handler pemrosesan file masuk dengan validasi ukuran & keamanan
async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_file = update.message.document
    
    # 1. Validasi ukuran file
    if user_file.file_size > MAX_FILE_SIZE:
        await update.message.reply_text("❌ Maaf, ukuran file terlalu besar! Batas maksimal adalah **20 MB**.", parse_mode="Markdown")
        return

    file_name = user_file.file_name
    file_ext = file_name.split('.')[-1].lower()

    status_msg = await update.message.reply_text(
        f"⏳ Menerima file `_{file_name}_`.\nSedang memproses konversi, mohon tunggu sebentar...", 
        parse_mode="Markdown"
    )

    os.makedirs("./downloads", exist_ok=True)
    input_path = f"./downloads/{file_name}"
    output_path = "./downloads/"
    base_name = os.path.splitext(file_name)[0]
    result_file = None

    try:
        file = await context.bot.get_file(user_file.file_id)
        await file.download_to_drive(input_path)

        office_to_pdf_formats = [
            'docx', 'doc', 'odt', 'rtf', 'txt', 
            'xlsx', 'xls', 'csv', 'ods', 
            'pptx', 'ppt', 'odp'
        ]

        # 2. Logika Konversi Office ke PDF
        if file_ext in office_to_pdf_formats:
            cmd = ["libreoffice", "--headless", "--convert-to", "pdf", input_path, "--outdir", output_path]
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            result_file = f"{output_path}{base_name}.pdf"

        # 3. Logika Konversi PDF ke Word
        elif file_ext == 'pdf':
            from pdf2docx import Converter
            result_file = f"{output_path}{base_name}.docx"
            cv = Converter(input_path)
            cv.convert(result_file, start=0, end=None)
            cv.close()

        else:
            await status_msg.edit_text("❌ Maaf, format file tersebut belum didukung.")
            return

        # Kirim hasil konversi jika file berhasil dibuat
        if result_file and os.path.exists(result_file):
            await update.message.reply_document(
                document=open(result_file, 'rb'), 
                caption="✅ Berhasil dikonversi oleh bot!"
            )
            await status_msg.delete()
        else:
            raise Exception("Gagal menghasilkan file keluaran konversi.")

    except Exception as e:
        # Fallback khusus jika PDF gagal dikonversi via modul biasa, coba ke XLSX/PPTX via LibreOffice
        try:
            if file_ext == 'pdf':
                target_ext = 'pptx' if 'ppt' in update.effective_message.text.lower() else 'xlsx'
                cmd = ["libreoffice", "--headless", "--convert-to", target_ext, input_path, "--outdir", output_path]
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                result_file = f"{output_path}{base_name}.{target_ext}"
                
                if os.path.exists(result_file):
                    await update.message.reply_document(document=open(result_file, 'rb'), caption=f"✅ Berhasil dikonversi ke {target_ext.upper()}!")
                    await status_msg.delete()
                else:
                    raise Exception("Format target tidak valid.")
            else:
                raise e
        except Exception as inner_e:
            await status_msg.edit_text(f"⚠️ Terjadi kesalahan saat memproses file: `{str(inner_e)}`", parse_mode="Markdown")
    
    finally:
        # 4. Pembersihan file lokal secara aman (Cleanup)
        if os.path.exists(input_path):
            os.remove(input_path)
        if result_file and os.path.exists(result_file):
            os.remove(result_file)

async def main():
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN belum diatur di file .env!")
        exit(1)

    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("🤖 Bot Telegram Converter Production-Ready siap berjalan...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    
    stop_signal = asyncio.get_event_loop().create_future()
    await stop_signal

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🤖 Bot dihentikan.")