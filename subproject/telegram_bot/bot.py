import os
import telebot
from telebot import types
import requests

# Mapping Russian zodiac names to English for the API
RU_TO_EN = {
    "Овен": "Aries",
    "Телец": "Taurus",
    "Близнецы": "Gemini",
    "Рак": "Cancer",
    "Лев": "Leo",
    "Дева": "Virgo",
    "Весы": "Libra",
    "Скорпион": "Scorpio",
    "Стрелец": "Sagittarius",
    "Козерог": "Capricorn",
    "Водолей": "Aquarius",
    "Рыбы": "Pisces",
}
# Mapping Russian day words to API values
RU_DAY_TO_EN = {
    "СЕГОДНЯ": "TODAY",
    "ЗАВТРА": "TOMORROW",
    "ВЧЕРА": "YESTERDAY",
}

# Hard‑coded token (embedded directly in the source as requested)
BOT_TOKEN = 'BOT_TOKEN'

bot = telebot.TeleBot(BOT_TOKEN)

def get_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('/start'), types.KeyboardButton('/hello'),
               types.KeyboardButton('/horoscope'), types.KeyboardButton('/help'))
    return markup

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Как дела?", reply_markup=get_menu_markup())

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Доступные команды:\n"
        "/start, /hello – приветствие\n"
        "/horoscope – гороскоп по знаку зодиака и дате\n"
        "/help – это меню\n"
        "/menu – показать клавиатуру с кнопками"
    )
    bot.send_message(message.chat.id, help_text, reply_markup=get_menu_markup())

@bot.message_handler(commands=['menu'])
def send_menu(message):
    bot.send_message(message.chat.id, "Выберите команду:", reply_markup=get_menu_markup())

@bot.message_handler(func=lambda msg: not msg.text.startswith('/'))
def echo_all(message):
    bot.send_message(message.chat.id, message.text, reply_markup=get_menu_markup())

def get_daily_horoscope(sign: str, day: str) -> dict:
    """Fetch daily horoscope from public API."""
    url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope/daily"
    params = {"sign": sign, "day": day}
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()

@bot.message_handler(commands=['horoscope'])
def sign_handler(message):
    text = (
        "Какой ваш знак зодиака?\n"
        "Выберите один: *Овен*, *Телец*, *Близнецы*, *Рак*, *Лев*, *Дева*, *Весы*, *Скорпион*, *Стрелец*, *Козерог*, *Водолей*, *Рыбы*."
    )
    sent_msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')
    bot.register_next_step_handler(sent_msg, day_handler)

def day_handler(message):
    sign = message.text.strip().capitalize()
    text = (
        "На какой день нужен гороскоп?\n"
        "Выберите: *СЕГОДНЯ*, *ЗАВТРА*, *ВЧЕРА* или дату в формате ГГГГ‑ММ‑ДД."
    )
    sent_msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')
    bot.register_next_step_handler(sent_msg, fetch_horoscope, sign)

def fetch_horoscope(message, sign):
    day = message.text.strip().upper()
    try:
        data = get_daily_horoscope(sign, day)
        horoscope = data.get('data', {}).get('horoscope', data.get('data', {}).get('horoscope_data', 'Нет данных'))
        date_str = data.get('data', {}).get('date', '')
        reply = f"*Гороскоп:* {horoscope}\n*Знак:* {sign}\n*Дата:* {date_str}"
        bot.send_message(message.chat.id, "Вот ваш гороскоп:")
        bot.send_message(message.chat.id, reply, parse_mode='Markdown')
    except Exception as e:
        bot.send_message(message.chat.id, f"Не удалось получить гороскоп: {e}")

if __name__ == '__main__':
    bot.infinity_polling()
