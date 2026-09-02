import telebot
import time

# === НАСТРОЙКИ ===
TOKEN = "8610638568:AAHe7Xvlxi_UGKjEjSKlpjrHsZuF_PySX8s"
bot = telebot.TeleBot(TOKEN)

# === ОБРАБОТЧИКИ КОМАНД ===
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
        "🧠 Добро пожаловать в Neuro Biz AI!\n\n"
        "Ваш личный ИИ-ассистент для бизнеса.\n"
        "📦 Скачать: https://github.com/nemo94314-hub/neuro-biz-ai/releases/latest\n"
        "💳 Для покупки лицензионного ключа напишите /buy"
    )

@bot.message_handler(commands=['buy'])
def send_buy_info(message):
    bot.reply_to(message,
        "💰 Стоимость лицензии: $199 (~17 000 ₽)\n"
        "Для оплаты свяжитесь с нами: neurobizai@gmail.com\n"
        "После оплаты вы получите лицензионный ключ."
    )

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message,
        "Доступные команды:\n"
        "/start — приветствие и ссылка на скачивание\n"
        "/buy — информация о покупке лицензии\n"
        "/help — этот список команд"
    )

# === ЗАПУСК БОТА ===
print("Бот Neuro Biz AI запущен...")
bot.infinity_polling()
