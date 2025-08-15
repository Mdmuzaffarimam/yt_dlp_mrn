
import os
import re
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List

from telegram import (
    Update, InlineKeyboardMarkup, InlineKeyboardButton, InputFile
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from yt_dlp import YoutubeDL

# ----------------------
# Set your bot token here directly or via environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN", "PUT_YOUR_BOT_TOKEN_HERE")
MAX_MB = int(os.getenv("MAX_DOWNLOAD_SIZE_MB", "1900"))
COOKIES_FILE = "cookies.txt"

if not BOT_TOKEN:
    raise SystemExit("BOT_TOKEN missing. Set it in the code or environment variable")

# ---- State ----
pending: Dict[int, Dict[str, Any]] = {}

# ---- Keyboards ----
def main_menu() -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton("🎥 Download Video", callback_data="menu:video"),
            InlineKeyboardButton("🎵 Download Audio", callback_data="menu:audio"),
            InlineKeyboardButton("📝 Subtitles", callback_data="menu:subs"),
        ],
        [
            InlineKeyboardButton("🖼 Thumbnail", callback_data="menu:thumb"),
            InlineKeyboardButton("✂ Trimmer", callback_data="menu:trim"),
            InlineKeyboardButton("🔗 Direct/Stream Link", callback_data="menu:direct"),
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="menu:cancel")]
    ]
    return InlineKeyboardMarkup(rows)

QUALITIES = [
    ("240p", 240), ("360p", 360), ("480p", 480), ("720p", 720),
    ("1080p", 1080), ("1440p", 1440), ("2160p", 2160)
]

def quality_menu() -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(t, callback_data=f"q:{h}") for t, h in QUALITIES[:3]],
        [InlineKeyboardButton(t, callback_data=f"q:{h}") for t, h in QUALITIES[3:6]],
        [InlineKeyboardButton("2160p", callback_data="q:2160"),
         InlineKeyboardButton("⬅ Back", callback_data="back:menu")]
    ]
    return InlineKeyboardMarkup(rows)

# ---- Helpers ----
def ensure_url(text: str) -> Optional[str]:
    if not text:
        return None
    text = text.strip()
    if any(x in text for x in ("youtube.com", "youtu.be")):
        return text
    return None

def ytdl_common_opts() -> Dict[str, Any]:
    opts: Dict[str, Any] = {
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "outtmpl": "%(title)s - %(id)s.%(ext)s",
        "merge_output_format": "mp4",
    }
    if os.path.exists(COOKIES_FILE):
        opts["cookiefile"] = COOKIES_FILE
    return opts

def size_mb(path: Path) -> float:
    return path.stat().st_size / (1024 * 1024)

async def safe_send_video(update_or_ctx, chat_id: int, file_path: Path, caption: str):
    try:
        await update_or_ctx.bot.send_video(
            chat_id=chat_id,
            video=open(file_path, "rb"),
            supports_streaming=True,
            caption=caption
        )
    finally:
        try: file_path.unlink()
        except: pass

# ---- Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "YouTube Suite Bot\n\n"
        "Features:\n• Video (240p–2160p)\n• Audio (MP3/M4A)\n• Subtitles\n• Thumbnail\n• Trimmer\n• Direct/Stream Link\n\n"
        "Send YouTube link first or tap a menu option.",
        reply_markup=main_menu()
    )

# ---- Other handlers same as before (on_text, on_menu, on_quality, do_audio, do_subtitles, do_thumbnail, do_trimmer, do_direct) ----
# For brevity, handlers omitted in this code snippet
# Use previous complete bot.py code and remove dotenv imports and load_dotenv calls

def build_app():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    # Add other handlers here as before
    return app

if __name__ == "__main__":
    app = build_app()
    app.run_polling()
