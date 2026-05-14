import telebot
from telebot import types
import requests
from deep_translator import GoogleTranslator

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

RU_PERIOD_TO_EN = {
    "🌞 Сегодняшний": "daily",
    "📅 Недельный": "weekly",
    "🗓 Месячный": "monthly",
}

BOT_TOKEN = 'BOT_TOKEN'

bot = telebot.TeleBot(BOT_TOKEN)

def get_menu_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(
        types.KeyboardButton('👋 Привет'),
        types.KeyboardButton('🔮 Гороскоп'),
        types.KeyboardButton('📋 Помощь'),
        types.KeyboardButton('📌 Меню'),
    )
    return markup

def get_day_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    markup.add(
        types.KeyboardButton('🌞 Сегодняшний'),
        types.KeyboardButton('📅 Недельный'),
        types.KeyboardButton('🗓 Месячный'),
    )
    return markup

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.send_message(message.chat.id, "Привет! Как дела?", reply_markup=get_menu_markup())

@bot.message_handler(commands=['help'])
def send_help(message):
    help_text = (
        "Доступные кнопки:\n"
        "👋 Привет — приветствие\n"
        "🔮 Гороскоп — получить гороскоп по знаку зодиака\n"
        "📋 Помощь — это сообщение\n"
        "📌 Меню — показать клавиатуру"
    )
    bot.send_message(message.chat.id, help_text, reply_markup=get_menu_markup())

@bot.message_handler(commands=['menu'])
def send_menu(message):
    bot.send_message(message.chat.id, "Выберите команду:", reply_markup=get_menu_markup())

@bot.message_handler(commands=['horoscope'])
def sign_handler_cmd(message):
    _ask_sign(message)

@bot.message_handler(func=lambda msg: msg.text in ('👋 Привет', '🔮 Гороскоп', '📋 Помощь', '📌 Меню'))
def handle_buttons(message):
    if message.text == '👋 Привет':
        bot.send_message(message.chat.id, "Привет! Как дела?", reply_markup=get_menu_markup())
    elif message.text == '🔮 Гороскоп':
        _ask_sign(message)
    elif message.text == '📋 Помощь':
        help_text = (
            "Доступные кнопки:\n"
            "👋 Привет — приветствие\n"
            "🔮 Гороскоп — получить гороскоп по знаку зодиака\n"
            "📋 Помощь — это сообщение\n"
            "📌 Меню — показать клавиатуру"
        )
        bot.send_message(message.chat.id, help_text, reply_markup=get_menu_markup())
    elif message.text == '📌 Меню':
        bot.send_message(message.chat.id, "Выберите команду:", reply_markup=get_menu_markup())

@bot.message_handler(func=lambda msg: True)
def unknown_message(message):
    bot.send_message(
        message.chat.id,
        "🤔 Неизвестная команда.\n\n"
        "Попробуйте:\n"
        "🔮 Гороскоп\n"
        "📋 Помощь\n"
        "📌 Меню",
        reply_markup=get_menu_markup()
    )

def get_horoscope(sign: str, period: str) -> dict:
    url = f"https://freehoroscopeapi.com/api/v1/get-horoscope/{period}"
    params = {"sign": sign.lower()}
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()

def _ask_sign(message):
    text = (
        "Какой гороскоп хотите?n"
        "Выберите один: *Овен*, *Телец*, *Близнецы*, *Рак*, *Лев*, *Дева*, "
        "*Весы*, *Скорпион*, *Стрелец*, *Козерог*, *Водолей*, *Рыбы*."
    )
    sent_msg = bot.send_message(message.chat.id, text, parse_mode='Markdown')
    bot.register_next_step_handler(sent_msg, day_handler)

def day_handler(message):
    sign_ru = message.text.strip().capitalize()

    if sign_ru not in RU_TO_EN:
        bot.send_message(
            message.chat.id,
            "Знак не распознан. Введите знак из списка, например: Лев, Весы, Рак.",
            reply_markup=get_menu_markup()
        )
        return

    sent_msg = bot.send_message(
        message.chat.id,
        "На какой день нужен гороскоп?",
        reply_markup=get_day_markup()
    )
    bot.register_next_step_handler(sent_msg, fetch_horoscope, sign_ru)

def fetch_horoscope(message, sign_ru):
    period_input = message.text.strip()

    if period_input not in RU_PERIOD_TO_EN:
        sent_msg = bot.send_message(
            message.chat.id,
            "Пожалуйста, выберите тип гороскопа кнопками ниже.",
            reply_markup=get_day_markup()
        )
        bot.register_next_step_handler(sent_msg, fetch_horoscope, sign_ru)
        return

    period_en = RU_PERIOD_TO_EN[period_input]
    sign_en = RU_TO_EN.get(sign_ru)

    if not sign_en:
        bot.send_message(
            message.chat.id,
            "Не удалось определить знак зодиака.",
            reply_markup=get_menu_markup()
        )
        return

    try:
        data = get_horoscope(sign_en, period_en)

        inner = data.get('data', {})

        horoscope = (
            inner.get('horoscope')
            or inner.get('description')
            or inner.get('text')
        )

        if not horoscope:
            bot.send_message(
                message.chat.id,
                f"Ответ API: {inner}",
                reply_markup=get_menu_markup()
            )
            return

        try:
            horoscope = GoogleTranslator(
                source='en',
                target='ru'
            ).translate(horoscope)
        except Exception:
            pass

        date_str = inner.get('date', '')
        period_name = period_input.replace('🌞 ', '').replace('📅 ', '').replace('🗓 ', '')

        reply = (
            f"*{period_name} гороскоп*\n\n"
            f"*Знак:* {sign_ru}\n"
            f"*Дата:* {date_str}\n\n"
            f"{horoscope}"
        )

        bot.send_message(
            message.chat.id,
            "🔮 Вот ваш гороскоп:"
        )

        bot.send_message(
            message.chat.id,
            reply,
            parse_mode='Markdown',
            reply_markup=get_menu_markup()
        )

    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"Не удалось получить гороскоп: {e}",
            reply_markup=get_menu_markup()
        )
if __name__ == '__main__':
    bot.infinity_polling()