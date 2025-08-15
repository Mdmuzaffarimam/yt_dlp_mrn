
import os
import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from yt_dlp import YoutubeDL

BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
COOKIES_FILE = "cookies.txt"
MAX_MB = int(os.getenv("MAX_DOWNLOAD_SIZE_MB", "1900"))

QUALITIES = [("240p", 240), ("360p", 360), ("480p", 480),
             ("720p", 720), ("1080p", 1080), ("1440p", 1440), ("2160p", 2160)]

def quality_menu():
    rows = [
        [InlineKeyboardButton(t, callback_data=f"q:{h}") for t, h in QUALITIES[:3]],
        [InlineKeyboardButton(t, callback_data=f"q:{h}") for t, h in QUALITIES[3:6]],
        [InlineKeyboardButton("2160p", callback_data="q:2160")]
    ]
    return InlineKeyboardMarkup(rows)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome! Send a YouTube link.", reply_markup=quality_menu())

def ytdl_opts():
    opts = {"noplaylist": True, "quiet": True, "merge_output_format": "mp4"}
    if os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    return opts

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("Invalid YouTube URL.")
        return
    await update.message.reply_text("Processing...")
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, download_video, url, update, context)

def download_video(url, update, context):
    ydl_opts = ytdl_opts()
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        # For demo, not sending actual file here
        asyncio.run_coroutine_threadsafe(
            update.message.reply_text(f"Downloaded: {info.get('title')}"), context.application.loop
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.run_polling()
