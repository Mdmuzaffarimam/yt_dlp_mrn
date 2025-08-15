
import os
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_DOWNLOAD_SIZE_MB = int(os.getenv("MAX_DOWNLOAD_SIZE_MB", 1900))

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set. Please configure it in .env file.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a YouTube link and I'll download the video in best quality (up to 4K).")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    await update.message.reply_text(f"Downloading video from: {url}")

    try:
        ydl_opts = {
            'format': 'bestvideo[height<=2160]+bestaudio/best',
            'outtmpl': '%(title)s.%(ext)s',
            'merge_output_format': 'mp4',
            'noplaylist': True,
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            file_size = info.get('filesize') or info.get('filesize_approx', 0)
            if file_size and file_size > MAX_DOWNLOAD_SIZE_MB * 1024 * 1024:
                await update.message.reply_text("⚠️ Video is too large for Telegram upload.")
                return
            ydl.download([url])
            file_name = ydl.prepare_filename(info)

        await update.message.reply_video(video=open(file_name, 'rb'))
        os.remove(file_name)

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    app.run_polling()

if __name__ == "__main__":
    main()
