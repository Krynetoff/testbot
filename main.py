import sqlite3
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота (замените на свой)
BOT_TOKEN = ""


# Инициализация базы данных
def init_db():
    conn = sqlite3.connect('messages.db')
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
    conn = sqlite3.connect('messages.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO messages (user_id, username, message_text, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, username, message_text, datetime.now()))
    conn.commit()
    conn.close()


# Функция для получения последних 10 записей
def get_last_messages(limit=10):
    conn = sqlite3.connect('messages.db')
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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот, который записывает все сообщения в базу данных. "
        "Просто отправь мне любое сообщение, и я его сохраню.\n"
        "Используй команду /records чтобы посмотреть последние 10 записей."
    )


# Обработчик команды /records
async def show_records(update: Update, context: ContextTypes.DEFAULT_TYPE):
    messages = get_last_messages()

    if not messages:
        await update.message.reply_text("В базе данных пока нет записей.")
        return

    response = "📝 Последние 10 записей:\n\n"
    for i, (username, message_text, timestamp) in enumerate(messages, 1):
        # Форматируем timestamp для красивого отображения
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S.%f')
        formatted_time = dt.strftime('%d.%m.%Y %H:%M')

        response += f"{i}. 👤 {username}\n"
        response += f"   💬 {message_text}\n"
        response += f"   🕒 {formatted_time}\n\n"

    await update.message.reply_text(response)


# Обработчик текстовых сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or f"user_{user_id}"
    message_text = update.message.text

    # Сохраняем сообщение в базу данных
    save_message(user_id, username, message_text)

    # Отправляем ответ пользователю
    await update.message.reply_text("✅ Все записал")


# Основная функция
def main():
    # Инициализируем базу данных
    init_db()

    # Создаем приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("records", show_records))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Бот запущен...")
    application.run_polling()


if __name__ == '__main__':
    main()