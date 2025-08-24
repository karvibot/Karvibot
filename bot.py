import telebot
import os

API_TOKEN = os.environ.get("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN не найден! Проверь Environment Variables.")

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(
        message, 
        "Привет 👋 Я твой контент-бот! Напиши: пост, Reels или сторис, и я помогу ✨"
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.lower()

    if "пост" in text:
        bot.reply_to(message, "✍️ Шаблон поста:\n1. Крючок\n2. История/боль\n3. Решение\n4. Призыв к действию")
    elif "рилс" in text or "reels" in text:
        bot.reply_to(message, "🎬 Пример сценария Reels:\n1. Вступление — боль\n2. Поворот\n3. Короткое решение\n4. Концовка")
    elif "сторис" in text:
        bot.reply_to(message, "📱 Идея для сторис:\n— Вопрос аудитории\n— Ваш честный ответ\n— Визуальный акцент")
    else:
        bot.reply_to(message, "Я пока учусь 😉 Скажи: пост, Reels или сторис?")

bot.polling(none_stop=True)
