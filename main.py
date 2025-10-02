import telebot
import time
import os
# from dotenv import load_dotenv

# BOT_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

@bot.message_handler(content_types=['text'])
def echo_message(message):
    try:
        # Добавляем небольшую задержку для имитации "думающего" бота
        time.sleep(1)
        bot.send_message(message.chat.id, f"Вы написали: {message.text}")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == '__main__':
    print("Бот запущен...")
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            time.sleep(15)