import telebot
import sqlite3
import logging
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from config import token  # Импортируем токен из config.py

# --- Настройка логирования ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Константы ---
BOT_TOKEN = token  # Используем импортированный токен
DATABASE_NAME = 'support_bot.db'
ADMIN_USER_ID = 'YOUR_ADMIN_USER_ID'  # Замените на ID админа (для команд типа /add_faq)

# --- Инициализация бота ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- Подключение к базе данных ---
def connect_to_db():
    try:
        conn = sqlite3.connect(DATABASE_NAME)
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        logging.error(f"Ошибка подключения к базе данных: {e}")
        return None, None

# --- Создание таблиц в базе данных (если их нет) ---
def create_tables():
    conn, cursor = connect_to_db()
    if not conn:
        return

    try:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS faq (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT UNIQUE NOT NULL,
                answer TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS support_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                question TEXT,
                answer TEXT,
                manager_id INTEGER,
                status TEXT DEFAULT 'new',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS managers (
                user_id INTEGER PRIMARY KEY
            )
        ''')

        conn.commit()
        logging.info("Таблицы созданы или уже существуют.")

    except sqlite3.Error as e:
        logging.error(f"Ошибка при создании таблиц: {e}")

    finally:
        if conn:
            conn.close()

# --- Загрузка данных из FAQ и добавление в базу, если их нет ---
def initialize_faq():
    conn, cursor = connect_to_db()
    if not conn:
        return

    faq_data = [
        ("Как оформить заказ?",
         "Для оформления заказа, пожалуйста, выберите интересующий вас товар и нажмите кнопку \"Добавить в корзину\", затем перейдите в корзину и следуйте инструкциям для завершения покупки."),
        ("Как узнать статус моего заказа?",
         "Вы можете узнать статус вашего заказа, войдя в свой аккаунт на нашем сайте и перейдя в раздел \"Мои заказы\". Там будет указан текущий статус вашего заказа."),
        ("Как отменить заказ?",
         "Если вы хотите отменить заказ, пожалуйста, свяжитесь с нашей службой поддержки как можно скорее. Мы постараемся помочь вам с отменой заказа до его отправки."),
        ("Что делать, если товар пришел поврежденным?",
         "При получении поврежденного товара, пожалуйста, сразу свяжитесь с нашей службой поддержки и предоставьте фотографии повреждений. Мы поможем вам с обменом или возвратом товара."),
        ("Как связаться с вашей технической поддержкой?",
         "Вы можете связаться с нашей технической поддержкой через телефон на нашем сайте или написать нам в чат-бота."),
        ("Как узнать информацию о доставке?",
         "Информацию о доставке вы можете найти на странице оформления заказа на нашем сайте. Там указаны доступные способы доставки и сроки.")
    ]

    try:
        for question, answer in faq_data:
            cursor.execute("SELECT 1 FROM faq WHERE question = ?", (question,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO faq (question, answer) VALUES (?, ?)", (question, answer))
                logging.info(f"Добавлен вопрос в FAQ: {question}")
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при инициализации FAQ: {e}")
    finally:
        if conn:
            conn.close()

# --- Функции для работы с FAQ ---
def load_faq():
    faq_dict = {}
    conn, cursor = connect_to_db()
    if not conn:
        return faq_dict

    try:
        cursor.execute("SELECT question, answer FROM faq")
        rows = cursor.fetchall()
        for row in rows:
            faq_dict[row[0]] = row[1]
        logging.info("FAQ загружен из базы данных.")
    except sqlite3.Error as e:
        logging.error(f"Ошибка при загрузке FAQ: {e}")
    finally:
        if conn:
            conn.close()
    return faq_dict

def get_faq_keyboard():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for question in faq:
        markup.add(KeyboardButton(question))
    markup.add(KeyboardButton("Написать свой вопрос"))  # Добавлена кнопка "Написать свой вопрос"
    return markup

# --- Функции для работы с запросами техподдержки ---
def save_request(user_id, question, answer=None, manager_id=None, status='new'):
    conn, cursor = connect_to_db()
    if not conn:
        return None

    try:
        cursor.execute('''
            INSERT INTO support_requests (user_id, question, answer, manager_id, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, question, answer, manager_id, status))
        conn.commit()
        request_id = cursor.lastrowid
        logging.info(f"Сохранен запрос от пользователя {user_id}. ID запроса: {request_id}")
        return request_id
    except sqlite3.Error as e:
        logging.error(f"Ошибка при сохранении запроса: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_request_by_id(request_id):
    conn, cursor = connect_to_db()
    if not conn:
        return None
    try:
        cursor.execute("SELECT * FROM support_requests WHERE id = ?", (request_id,))
        return cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении запроса по ID: {e}")
        return None
    finally:
        if conn:
            conn.close()

def get_managers():
    conn, cursor = connect_to_db()
    managers = set()
    if not conn:
        return managers
    try:
        cursor.execute("SELECT user_id FROM managers")
        rows = cursor.fetchall()
        managers = {row[0] for row in rows}
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении списка менеджеров: {e}")
    finally:
        if conn:
            conn.close()
    return managers

def get_manager_requests(manager_id):
    conn, cursor = connect_to_db()
    requests = []
    if not conn:
        return requests
    try:
        cursor.execute("SELECT id, question, user_id FROM support_requests WHERE manager_id = ? AND answer IS NULL", (manager_id,))
        requests = cursor.fetchall() # Returns a list of tuples: (id, question, user_id)
    except sqlite3.Error as e:
        logging.error(f"Ошибка при получении запросов менеджера: {e}")
    finally:
        if conn:
            conn.close()
    return requests

def get_manager_keyboard(manager_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Ответить на вопрос"))
    return markup

def get_requests_keyboard(manager_id):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    requests = get_manager_requests(manager_id)
    if not requests:
        markup.add(KeyboardButton("Нет новых вопросов"))
    else:
        for request_id, question, user_id in requests:
            markup.add(KeyboardButton(f"Ответить на вопрос (ID: {request_id})"))
    markup.add(KeyboardButton("Вернуться"))
    return markup

# --- Обработчики команд и сообщений ---
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if user_id in get_managers():
        bot.send_message(message.chat.id, "Привет, менеджер! Готовы отвечать на вопросы?", reply_markup=get_manager_keyboard(user_id))
    else:
        bot.send_message(message.chat.id, "Привет! Я бот техподдержки. Выберите вопрос из списка или напишите свой.", reply_markup=get_faq_keyboard())

@bot.message_handler(commands=['menejinbot'])
def add_manager(message):
    user_id = message.from_user.id
    conn, cursor = connect_to_db()
    if not conn:
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")
        return

    try:
        cursor.execute("INSERT OR IGNORE INTO managers (user_id) VALUES (?)", (user_id,))
        conn.commit()
        bot.send_message(message.chat.id, "Вы добавлены в список менеджеров.")
        logging.info(f"Менеджер добавлен: {user_id}")
        bot.send_message(message.chat.id, "Привет, менеджер! Готовы отвечать на вопросы?", reply_markup=get_manager_keyboard(user_id)) # send manager keyboard
    except sqlite3.Error as e:
        logging.error(f"Ошибка при добавлении менеджера: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")
    finally:
        if conn:
            conn.close()

@bot.message_handler(func=lambda message: message.text in faq)
def handle_faq_question(message):
    answer = faq.get(message.text)
    if answer:
        bot.send_message(message.chat.id, answer, reply_markup=get_faq_keyboard())
        save_request(message.from_user.id, message.text, answer)  # Сохраняем вопрос и ответ
    else:
        bot.send_message(message.chat.id, "Извините, я не знаю ответа на этот вопрос.", reply_markup=get_faq_keyboard())

@bot.message_handler(func=lambda message: message.text == "Написать свой вопрос")
def ask_custom_question(message):
    bot.send_message(message.chat.id, "Пожалуйста, опишите свой вопрос.", reply_markup=telebot.types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, process_custom_question)

def process_custom_question(message):
    question = message.text
    managers = get_managers()
    if not managers:
        bot.send_message(message.chat.id, "В данный момент нет доступных менеджеров.", reply_markup=get_faq_keyboard())
        save_request(message.from_user.id, question) # Сохраняем вопрос без менеджера
        return

    # Отправляем вопрос случайному менеджеру
    import random
    manager_id = random.choice(list(managers))
    request_id = save_request(message.from_user.id, question, manager_id=manager_id) # сохраняем вопрос и ID менеджера
    if request_id:
        bot.send_message(message.chat.id, "Ваш вопрос отправлен менеджеру. Пожалуйста, ожидайте ответа.", reply_markup=get_faq_keyboard())
        bot.send_message(manager_id, f"Новый вопрос от пользователя {message.from_user.id} (ID запроса: {request_id}):\n{question}", reply_markup = get_manager_keyboard(manager_id))  # Отправляем вопрос менеджеру

        logging.info(f"Вопрос #{request_id} отправлен менеджеру {manager_id}")

    else:
        bot.send_message(message.chat.id, "Произошла ошибка при отправке вопроса.", reply_markup=get_faq_keyboard())

@bot.message_handler(func=lambda message: message.text == "Ответить на вопрос" and message.from_user.id in get_managers())
def answer_question(message):
    manager_id = message.from_user.id
    bot.send_message(message.chat.id, "Выберите вопрос, на который хотите ответить:", reply_markup=get_requests_keyboard(manager_id))

@bot.message_handler(func=lambda message: message.text.startswith("Ответить на вопрос (ID:") and message.from_user.id in get_managers())
def process_answer_selection(message):
    try:
        manager_id = message.from_user.id
        request_id = int(message.text.split('(ID: ')[1].split(')')[0])
        request = get_request_by_id(request_id)
        if not request or request[4] != manager_id:
            bot.send_message(message.chat.id, "Неверный ID запроса или у вас нет прав на ответ.", reply_markup=get_manager_keyboard(manager_id))
            return

        bot.send_message(message.chat.id, f"Ответьте на вопрос:\n{request[2]}", reply_markup=telebot.types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, process_manager_response, request_id) # register request_id

    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат ID запроса.", reply_markup=get_manager_keyboard(manager_id))

def process_manager_response(message, request_id):
    manager_id = message.from_user.id
    answer = message.text
    request = get_request_by_id(request_id)
    if not request or request[4] != manager_id:
        bot.send_message(message.chat.id, "Неверный ID запроса или у вас нет прав на ответ.", reply_markup=get_manager_keyboard(manager_id))
        return

    user_id = request[1]
    save_request(user_id, request[2], answer, manager_id, 'resolved') # update with an answer

    bot.send_message(user_id, f"Ответ от менеджера:\n{answer}", reply_markup=get_faq_keyboard()) # Send answer
    bot.send_message(message.chat.id, "Ответ отправлен пользователю.", reply_markup=get_manager_keyboard(manager_id)) # Notify manager

@bot.message_handler(func=lambda message: message.text == "Вернуться" and message.from_user.id in get_managers())
def back_to_manager_menu(message):
    manager_id = message.from_user.id
    bot.send_message(message.chat.id, "Возвращаюсь в основное меню менеджера.", reply_markup=get_manager_keyboard(manager_id))

@bot.message_handler(func=lambda message: message.text == "Нет новых вопросов" and message.from_user.id in get_managers())
def no_new_requests(message):
    manager_id = message.from_user.id
    bot.send_message(message.chat.id, "Нет новых запросов. Ожидайте.", reply_markup=get_manager_keyboard(manager_id))
#--- Default response
@bot.message_handler(func=lambda message: True)
def default_response(message):
  user_id = message.from_user.id
  if user_id in get_managers():
      bot.send_message(message.chat.id, "Используйте кнопки или выберите вопрос.", reply_markup=get_manager_keyboard(user_id))
  else:
      bot.send_message(message.chat.id, "Используйте кнопки или выберите вопрос.", reply_markup=get_faq_keyboard())

# --- Загрузка FAQ при старте и инициализация базы данных ---
create_tables()
initialize_faq()
faq = load_faq()

# --- Запуск бота ---
if __name__ == '__main__':
    logging.info("Бот запущен.")
    bot.infinity_polling()