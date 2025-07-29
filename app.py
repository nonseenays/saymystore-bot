import telebot
import random

API_TOKEN = "8203843422:AAF24yiyOCRwJD7xDCifH6cGC42RIcrgnyE"
bot = telebot.TeleBot(API_TOKEN)

USDT_RATE = 90  # курс рублей к USDT

prices_rub = {
    "MDMA 1Г": 3090,
    "AMF 1Г": 2990,
    "MEPHEDRONE 1Г": 2490,
    "MEPHEDRONE 2Г": 4550,
    "EXTAZI 2ШТ": 2590,
    "EXTAZI 3ШТ": 3550,
    "РОСС (СПАЙС) 2Г": 2490,
    "РОСС (СПАЙС) 3Г": 3490,
    "LSD (170MKG) 2ШТ": 3490,
    "MED 0.5 Г": 3490,
    "MED 1 Г": 6490,
    "ГАШ DIAMOND HAZE 1Г": 2490,
    "ГАШ DIAMOND HAZE 2Г": 4590,
    "ГАШ ЕВРО 1Г": 2990,
    "МАРИХАУННА/ 1г": 2590,
    "МАРИХУАННА/ 2г": 4520,
    "CK APVP 1г": 2540,
    "ЛИРИКА ( Pfizer 300 mg ) - 28 шт": 3540,
    "ЛИРИКА ( Prizer 300 mg ) - 56 шт": 6550,
    "ПРЕГАБАЛИН ( Rixter 300 mg ) - 28 шт": 3520,
    "ПРЕГАБАЛИН ( Rixter 300 mg ) - 56 шт": 6490,
    "ГАШ ЕВРО - 2г": 5490,
    "Гер.WHITE - 1г": 3490,
    "Шишки Og kush - 1г": 2490,
    "Шишки 0g kush - 2г": 4590,
    "KOKAIN (BOLIVIA) - 0.5г": 5090,
    "KOKAIN (BOLIVIA) - 1г": 10100,
    "МЕФЕДРОН ( Кристаллы ) - 0.5 г": 2590,
    "МЕФЕДРОН ( Кристаллы ) - 1г": 4490,
    "АНАША - 1г": 2590,
    "АНАША - 2г": 4490,
}

cities = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань",
    "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону",
    "Уфа", "Красноярск", "Воронеж", "Пермь", "Волгоград",
    "Краснодар", "Саратов", "Тюмень", "Тольятти", "Ижевск",
    "Барнаул", "Ульяновск", "Иркутск", "Хабаровск", "Ярославль",
    "Владивосток", "Махачкала", "Томск", "Оренбург", "Кемерово"
]

usdt_address = "TLXpo31Ws8PzAXHNBX3CYXuu5FEXoabptJ"
user_orders = {}

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🐲 ОФОРМИТЬ ЗАКАЗ 🐲")
    bot.send_message(message.chat.id, "Добро пожаловать в SayMyStore. 💛\nВыберите действие:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "🐲 ОФОРМИТЬ ЗАКАЗ 🐲")
def choose_city(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    for city_chunk in chunk_list(cities, 3):
        markup.add(*city_chunk)
    bot.send_message(message.chat.id, "Выберите город:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in cities)
def choose_product(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=4)
    for product_chunk in chunk_list(list(prices_rub.keys()), 4):
        markup.add(*product_chunk)
    bot.send_message(message.chat.id, "Выберите товар:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in prices_rub)
def product_choice(message):
    chat_id = message.chat.id
    user_orders[chat_id] = {
        'product': message.text,
        'city': None,
        'delivery_method': None,
        'order_number': random.randint(1000, 9999)
    }
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Магнит", "Прикоп", "Тайник")
    bot.send_message(chat_id, f"Вы выбрали товар: {message.text}\nВыберите способ получения:", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["Магнит", "Прикоп", "Тайник"])
def choose_delivery(message):
    chat_id = message.chat.id
    if chat_id not in user_orders or 'product' not in user_orders[chat_id]:
        bot.send_message(chat_id, "Пожалуйста, сначала выберите товар.")
        return

    user_orders[chat_id]['delivery_method'] = message.text
    product = user_orders[chat_id]['product']
    price_rub = prices_rub[product]
    price_usdt = round(price_rub / USDT_RATE, 2)
    order_number = user_orders[chat_id]['order_number']

    pay_text = (
        f"Ваш заказ:\n"
        f"Товар: {product}\n"
        f"Способ получения: {message.text}\n"
        f"Сумма: {price_rub} ₽\n"
        f"Оплата в USDT (TRC20): {price_usdt} USDT\n\n"
        f"Адрес для оплаты:\n{usdt_address}\n\n"
        f"Номер заказа: {order_number}\n\n"
        f"Нажмите кнопку ниже, чтобы скопировать адрес оплаты."
    )

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            text="Скопировать адрес оплаты",
            callback_data=f"copy_payment_{order_number}_{price_usdt}"
        )
    )

    bot.send_message(chat_id, pay_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_payment_"))
def callback_copy_payment_info(call):
    data = call.data.split("_")
    order_number = data[2]
    price_usdt = data[3]
    chat_id = call.message.chat.id

    text = (
        f"Адрес для оплаты:\n{usdt_address}\n"
        f"Сумма к оплате: {price_usdt} USDT\n"
        f"Номер заказа: {order_number}"
    )
    bot.send_message(chat_id, text)
    bot.answer_callback_query(call.id, "Адрес и номер заказа отправлены в чат.\nПосле оплаты подтвердите заказ командой /confirm")

@bot.message_handler(commands=['confirm'])
def confirm_order(message):
    chat_id = message.chat.id
    order = user_orders.get(chat_id)
    if not order or 'product' not in order or 'delivery_method' not in order:
        bot.send_message(chat_id, "У вас нет активного заказа.")
        return

    bot.send_message(chat_id,
                     f"Спасибо! Ваш заказ №{order['order_number']} принят и будет обработан.\n"
                     f"Товар: {order['product']}\n"
                     f"Способ получения: {order['delivery_method']}\n"
                     f"Мы свяжемся с вами в ближайшее время.")
    user_orders.pop(chat_id)

@bot.message_handler(func=lambda m: True)
def default_handler(message):
    bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки для навигации или /start для начала.")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)
