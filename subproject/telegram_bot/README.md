# Telegram Horoscope Bot (Python)

## Overview
This small bot demonstrates how to create a Telegram bot using **pyTelegramBotAPI**. It supports:
- `/start` and `/hello` – greeting messages.
- Echo of any text message.
- `/horoscope` – interactive flow that asks for a zodiac sign and a day, then returns a daily horoscope from a public API.

## Prerequisites
- Python 3.8+
- A Telegram bot token obtained from **@BotFather**.
- Internet connection (to call the horoscope API).

## Setup
1. Navigate to the bot directory:
   ```bash
   cd subproject/telegram_bot
   ```
2. (Recommended) Create a virtual environment:
   ```bash
   python -m venv venv
   # Activate:
   #   Linux/macOS: source venv/bin/activate
   #   Windows CMD: venv\Scripts\activate
   #   Windows PowerShell: .\venv\Scripts\Activate.ps1
   ```
3. Install dependencies **including** `python-dotenv`:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy the example environment file and add your token:
   ```bash
   cp .env.example .env
   # edit .env and replace the placeholder with the real token
   ```
   The bot reads the variable `BOT_TOKEN` from this file automatically.

## Running the bot
```bash
python bot.py
```
The bot will start polling Telegram servers. Open a chat with your bot and try the commands:
- `/start` – greeting.
- `/hello` – another greeting.
- `/horoscope` – follow the prompts to receive a horoscope.

## Project structure
```
telegram_bot/
├─ bot.py            # main bot implementation
├─ requirements.txt  # Python dependencies (pyTelegramBotAPI, requests, python-dotenv)
├─ .env.example      # template for environment variables
├─ README.md         # this file
└─ .gitkeep          # ensures folder exists in repository
```

## License
This example code is provided under the MIT license.

---
**Note:** If you see `ModuleNotFoundError: No module named 'dotenv'`, make sure you have installed the updated requirements (`pip install -r requirements.txt`) and that you are using the virtual environment where they were installed.
