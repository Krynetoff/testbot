import sqlite3
import logging
import os
from datetime import datetime
import telebot

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (замените на свой)
# BOT_TOKEN = ""

# Создаем экземпляр бота
# bot = telebot.TeleBot(BOT_TOKEN)
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('messages.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            message_text TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


# Функция для сохранения сообщения в базу данных
def save_message(user_id, username, message_text):
    conn = sqlite3.connect('messages.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (user_id, username, message_text, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, message_text, datetime.now()))
    conn.commit()
    conn.close()


# Функция для получения последних 10 записей
def get_last_messages(limit=10):
    conn = sqlite3.connect('messages.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT username, message_text, timestamp 
        FROM messages 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    messages = cursor.fetchall()
    conn.close()
    return messages


# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Привет! Я бот, который записывает все сообщения в базу данных. "
                 "Просто отправь мне любое сообщение, и я его сохраню.\n"
                 "Используй команду /records чтобы посмотреть последние 10 записей."
                 )


# Обработчик команды /records
@bot.message_handler(commands=['records'])
def show_records(message):
    messages = get_last_messages()

    if not messages:
        bot.reply_to(message, "В базе данных пока нет записей.")
        return

    response = "📝 Последние 10 записей:\n\n"
    for i, (username, message_text, timestamp) in enumerate(messages, 1):
        # Форматируем timestamp для красивого отображения
        try:
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        except ValueError:
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        formatted_time = dt.strftime('%d.%m.%Y %H:%M')

        response += f"{i}. 👤 {username or 'Без username'}\n"
        response += f"   💬 {message_text}\n"
        response += f"   🕒 {formatted_time}\n\n"

    bot.reply_to(message, response)


# Обработчик текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username or f"user_{user_id}"
    message_text = message.text

    # Сохраняем сообщение в базу данных
    save_message(user_id, username, message_text)

    # Отправляем ответ пользователю
    bot.reply_to(message, "✅ Все записал")


# Основная функция
def main():
    # Инициализируем базу данных
    init_db()

    # Запускаем бота
    print("Бот запущен...")
    bot.infinity_polling()


if __name__ == '__main__':
    main()