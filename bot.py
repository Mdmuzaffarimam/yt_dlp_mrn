import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

from yt_dlp import YoutubeDL

# Load .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MAX_MB = int(os.getenv("MAX_DOWNLOAD_SIZE_MB", "1900"))  # Telegram safe threshold
COOKIES_FILE = "cookies.txt"  # packed in project

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN is missing. Set it in .env or environment.")

# Per-chat state to store pending URL and chosen quality
pending = {}

QUALITIES = [
    ("240p", 240),
    ("360p", 360),
    ("480p", 480),
    ("720p", 720),
    ("1080p", 1080),
    ("1440p", 1440),
    ("2160p", 2160),  # 4K
]

def ytdl_opts(max_h: int):
    opts = {
        "format": f"bestvideo[height<={max_h}]+bestaudio/best[height<={max_h}]",
        "merge_output_format": "mp4",
        "noplaylist": True,
        "outtmpl": "%(title)s - %(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }
    if os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    return opts

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "YouTube 4K Downloader Bot\\n\\n"
        "Send any YouTube link. I will show quality options (240p–2160p). "
        "Small files I'll send to Telegram; very large files may exceed Telegram's 2GB limit."
    )

def quality_keyboard():
    row1 = [InlineKeyboardButton(t, callback_data=f"q:{h}") for t, h in QUALITIES[:4]]
    row2 = [InlineKeyboardButton(t, callback_data=f"q:{h}") for t, h in QUALITIES[4:]]
    return InlineKeyboardMarkup([row1, row2])

async def on_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    if "youtube.com" not in text and "youtu.be" not in text:
        await update.message.reply_text("Please send a valid YouTube link.")
        return
    chat_id = update.effective_chat.id
    pending[chat_id] = {"url": text}
    await update.message.reply_text("Choose quality:", reply_markup=quality_keyboard())

async def on_quality(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    chat_id = query.message.chat.id
    data = query.data
    if not data.startswith("q:"):
        return
    max_h = int(data.split(":")[1])
    url = pending.get(chat_id, {}).get("url")
    if not url:
        await query.edit_message_text("No URL found. Please send the YouTube link again.")
        return

    await query.edit_message_text(f"Downloading {max_h}p...")
    opts = ytdl_opts(max_h)

    def do_download():
        try:
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # get the merged filename
                fname = ydl.prepare_filename(info)
                if not Path(fname).exists():
                    p = Path(fname).with_suffix(".mp4")
                    if p.exists():
                        fname = str(p)
                return {"file": fname, "title": info.get("title")}
        except Exception as e:
            return {"error": str(e)}

    result = await asyncio.to_thread(do_download)

    if "error" in result:
        await query.edit_message_text(f"Error: {result['error']}")
        return

    fpath = Path(result["file"])
    size_mb = fpath.stat().st_size / (1024*1024)

    if size_mb > MAX_MB:
        await query.edit_message_text(
            f"File is {size_mb:.1f} MB (>{MAX_MB} MB). Too large for Telegram. "
            f"Please pick a lower quality like 720p/480p."
        )
        try: fpath.unlink()
        except: pass
        return

    await query.edit_message_text(f"Uploading ({size_mb:.1f} MB)...")
    try:
        await context.bot.send_video(chat_id=chat_id, video=open(fpath, "rb"), supports_streaming=True,
                                     caption=f"{result['title']} ({max_h}p)")
        await context.bot.send_message(chat_id=chat_id, text="Done ✅")
    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"Upload failed: {e}")
    finally:
        try: fpath.unlink()
        except: pass

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_link))
    app.add_handler(CallbackQueryHandler(on_quality))
    app.run_polling()

if __name__ == "__main__":
    main()
