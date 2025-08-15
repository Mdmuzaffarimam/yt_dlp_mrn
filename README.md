# Telegram YouTube 4K Downloader Bot (Quality Picker + Cookies)
- Quality options: 240p, 360p, 480p, 720p, 1080p, 1440p, 2160p
- Uses `cookies.txt` to bypass age/consent checks where legal
- Sends file to Telegram if <= 2GB, else asks to pick lower quality

## Setup (Local)
```
pip install -r requirements.txt
cp .env.example .env   # put your BOT_TOKEN
python bot.py
```

## Deploy (Render/Railway)
- Create service from this repo/zip
- Add env var `BOT_TOKEN`
- Start command: `python bot.py`
- Ensure ffmpeg is available (Dockerfile provided)
