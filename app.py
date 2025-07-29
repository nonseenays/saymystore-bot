from flask import Flask, request
import os
import telebot
import random

API_TOKEN = "8203843422:AAF24yiyOCRwJD7xDCifH6cGC42RIcrgnyE"
bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

USDT_RATE = 90  # курс рублей к USDT

prices_rub = {
    # Словарь с товарами и ценами (скопируй сюда из предыдущего кода)
    "MDMA 1Г": 3090,
    # ...
}

user_selected_product = {}

@app.route('/' + API_TOKEN, methods=['POST'])
def get_message():
    json_str = request.get_data().decode('UTF-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def webhook():
    return "I'm alive", 200

# Далее вставь весь код с хендлерами, как был в твоем боте, например:

@bot.message_handler(commands=['start'])
def send_welcome(message):
    # код с кнопкой "🐲 ОФОРМИТЬ ЗАКАЗ 🐲"
    pass

# И остальные хендлеры (скопируй из моего предыдущего сообщения)

if __name__ == "__main__":
    # НЕ запускаем bot.polling(), т.к. мы работаем с webhook
    app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
