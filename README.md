# Telegram YouTube 4K Downloader Bot

A Telegram bot to download YouTube videos up to 4K resolution using yt-dlp.

## Features
- Downloads highest quality video (up to 4K)
- Sends directly to Telegram chat (<= 2GB)
- /format command to choose max resolution
- Progress updates

## Quick Deploy

### Deploy to Render
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/yourusername/telegram-youtube-4k-bot)

### Deploy to Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/yourusername/telegram-youtube-4k-bot&envs=BOT_TOKEN,MAX_DOWNLOAD_SIZE_MB&optionalEnvs=MAX_DOWNLOAD_SIZE_MB)

## Local Setup
1. Clone this repo:
   ```bash
   git clone https://github.com/yourusername/telegram-youtube-4k-bot.git
   cd telegram-youtube-4k-bot
   ```
2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```
3. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Create `.env` from `.env.example` and set your BOT_TOKEN.
5. Run:
   ```bash
   python bot.py
   ```

## Docker
```bash
docker build -t yt-telegram-bot .
docker run --env BOT_TOKEN="your:token" yt-telegram-bot
```

## Legal Notice
Use only for videos you have permission to download.
