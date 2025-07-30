import telebot
import random
import requests

TOKEN = '8203843422:AAF24yiyOCRwJD7xDCifH6cGC42RIcrgnyE'  
response = requests.get(f'https://api.telegram.org/bot{TOKEN}/deleteWebhook')
print(response.json())# <<< ВСТАВЬ СЮДА СВОЙ ТОКЕН
bot = telebot.TeleBot(TOKEN)

USDT_RATE = 90
usdt_address = "TLXpo31Ws8PzAXHNBX3CYXuu5FEXoabptJ"
admin_chat_id = 6779729167  # ← замени на свой Telegram ID

user_orders = {}
payment_status = {}

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

def chunk_list(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

PRODUCTS_PER_PAGE = 7

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
    chat_id = message.chat.id
    user_orders.setdefault(chat_id, {})
    user_orders[chat_id]['city'] = message.text
    user_orders[chat_id]['page'] = 0
    send_products_page(chat_id, 0)

def send_products_page(chat_id, page):
    products = list(prices_rub.keys())
    max_page = (len(products) - 1) // PRODUCTS_PER_PAGE

    if page < 0 or page > max_page:
        return

    user_orders[chat_id]['page'] = page
    start_idx = page * PRODUCTS_PER_PAGE
    end_idx = start_idx + PRODUCTS_PER_PAGE
    products_page = products[start_idx:end_idx]

    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    markup.add(*products_page)

    nav_buttons = []
    if page > 0:
        nav_buttons.append("⬅️ Предыдущая страница")
    if page < max_page:
        nav_buttons.append("➡️ Следующая страница")
    if nav_buttons:
        markup.add(*nav_buttons)

    bot.send_message(chat_id, f"Выберите товар (страница {page + 1} из {max_page + 1}):", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["⬅️ Предыдущая страница", "➡️ Следующая страница"])
def navigate_products(message):
    chat_id = message.chat.id
    page = user_orders.get(chat_id, {}).get('page', 0)
    if message.text == "⬅️ Предыдущая страница":
        page -= 1
    elif message.text == "➡️ Следующая страница":
        page += 1
    send_products_page(chat_id, page)

@bot.message_handler(func=lambda m: m.text in prices_rub)
def product_choice(message):
    chat_id = message.chat.id
    if chat_id not in user_orders:
        bot.send_message(chat_id, "Пожалуйста, сначала выберите город.")
        return

    user_orders[chat_id]['product'] = message.text
    user_orders[chat_id]['delivery_method'] = None
    user_orders[chat_id]['order_number'] = random.randint(1000, 9999)

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
        f"Нажмите кнопку ниже после оплаты."
    )

    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(
        telebot.types.InlineKeyboardButton(
            text="Я оплатил товар",
            callback_data=f"paid_{order_number}"
        )
    )

    bot.send_message(chat_id, pay_text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("paid_"))
def callback_paid(call):
    chat_id = call.message.chat.id
    order_number = call.data.split("_")[1]

    if chat_id not in user_orders or user_orders[chat_id].get('order_number') != int(order_number):
        bot.answer_callback_query(call.id, "Заказ не найден или уже обработан.")
        return

    bot.send_message(chat_id,
                     "Пожалуйста, пришлите скриншот оплаты, чтобы мы могли проверить и подтвердить ваш заказ.")
    bot.answer_callback_query(call.id)

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    chat_id = message.chat.id
    if chat_id not in user_orders or 'product' not in user_orders[chat_id]:
        bot.send_message(chat_id, "У вас нет активного заказа.")
        return

    if payment_status.get(chat_id) == 'pending':
        bot.send_message(chat_id, "Мы уже получили ваш скриншот оплаты и проверяем его. Пожалуйста, дождитесь результата.")
        return

    payment_status[chat_id] = 'pending'
    bot.send_message(chat_id, "Скриншот оплаты получен. Оплата будет проверена в течение 10 минут. Ожидайте ответа менеджера.")

# --- Запуск бота ---
print("Бот запущен через polling...")
bot.polling(none_stop=True)
