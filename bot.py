import os
import telebot

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # или вставьте токен напрямую
bot = telebot.TeleBot(TOKEN)

# === КОМАНДА /start ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "🧠 *Neuro Biz AI*\n\n"
        "Ваш личный ИИ-ассистент для бизнеса.\n\n"
        "✅ Отвечает на вопросы в вашем стиле\n"
        "✅ Помогает с документами и письмами\n"
        "✅ Всё локально — данные никуда не уходят\n\n"
        "📦 *Скачать:*\n"
        "https://github.com/nemo94314-hub/neuro-biz-ai/releases/latest\n\n"
        "💳 Для покупки лицензии напишите /buy"
    )

# === КОМАНДА /buy ===
@bot.message_handler(commands=['buy'])
def send_buy_info(message):
    bot.reply_to(message,
        "💰 *Стоимость лицензии:* $199 (~17 000 ₽)\n\n"
        "📩 Для оплаты свяжитесь с нами:\n"
        "nemo94314@gmail.com\n\n"
        "После оплаты вы получите лицензионный ключ.\n\n"
        "📦 Скачать приложение:\n"
        "https://github.com/nemo94314-hub/neuro-biz-ai/releases/latest"
    )

# === КОМАНДА /help ===
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
        "🤖 *Доступные команды:*\n"
        "/start — приветствие и ссылка на скачивание\n"
        "/buy — информация о покупке лицензии\n"
        "/help — этот список команд\n\n"
        "🌐 Наш сайт: https://nemo94314-hub.github.io/neuro-biz-ai\n"
        "📩 Почта: nemo94314@gmail.com"
    )

# === ЗАПУСК БОТА ===
print("Бот Neuro Biz AI запущен...")
bot.infinity_polling()
