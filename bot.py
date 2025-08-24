import telebot
import os

API_TOKEN = os.environ.get("API_TOKEN")
if not API_TOKEN:
    raise ValueError("API_TOKEN не найден! Проверь Environment Variables.")

bot = telebot.TeleBot(API_TOKEN)

# Хранилище данных пользователей и проектов
data_store = {}

# Приветствие и помощь
help_text = """
Привет! 👋 Я твой контент-бот.

Команды:
- /project Название_проекта — выбрать или создать проект
- пост — шаблон поста
- reels — сценарий Reels
- сторис — идея для Stories
- /plan — создать контент-план на неделю
- /warmup — пример прогрева для подписчиков
- /show — показать сохранённый контент проекта
"""

# Старт и помощь
@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, help_text)

# Создание/выбор проекта
@bot.message_handler(commands=['project'])
def select_project(message):
    try:
        project_name = message.text.split(" ", 1)[1].strip()
    except IndexError:
        bot.reply_to(message, "❌ Укажи название проекта после команды /project")
        return

    user_id = str(message.from_user.id)
    if user_id not in data_store:
        data_store[user_id] = {}

    if project_name not in data_store[user_id]:
        data_store[user_id][project_name] = {
            "posts": [], "reels": [], "stories": [], "plans": [], "warmups": []
        }

    data_store[user_id]["current_project"] = project_name
    bot.reply_to(message, f"✅ Выбран проект: {project_name}\nТеперь можешь писать: пост, reels, сторис.")

# Показать сохранённый контент
@bot.message_handler(commands=['show'])
def show_content(message):
    user_id = str(message.from_user.id)
    if user_id not in data_store or "current_project" not in data_store[user_id]:
        bot.reply_to(message, "❌ Сначала выбери проект через /project Название_проекта")
        return

    project = data_store[user_id]["current_project"]
    content = data_store[user_id][project]
    response = f"📂 Контент для проекта {project}:\n\n"
    for key in ["posts", "reels", "stories", "plans", "warmups"]:
        response += f"{key.upper()}:\n"
        for i, item in enumerate(content[key], 1):
            response += f"{i}. {item}\n"
        if not content[key]:
            response += "— пусто —\n"
        response += "\n"
    bot.reply_to(message, response)

# Генерация контент-плана
@bot.message_handler(commands=['plan'])
def generate_plan(message):
    user_id = str(message.from_user.id)
    if user_id not in data_store or "current_project" not in data_store[user_id]:
        bot.reply_to(message, "❌ Сначала выбери проект через /project Название_проекта")
        return

    project = data_store[user_id]["current_project"]
    plan = (
        "📅 Контент-план на неделю:\n"
        "Пн: пост с личной историей\n"
        "Вт: сторис с опросом\n"
        "Ср: Reels с инсайтом\n"
        "Чт: пост с полезным советом\n"
        "Пт: сторис «лайфхак»\n"
        "Сб: Reels с кейсом\n"
        "Вс: пост с результатами недели"
    )
    data_store[user_id][project]["plans"].append(plan)
    bot.reply_to(message, plan)

# Генерация прогрева
@bot.message_handler(commands=['warmup'])
def generate_warmup(message):
    user_id = str(message.from_user.id)
    if user_id not in data_store or "current_project" not in data_store[user_id]:
        bot.reply_to(message, "❌ Сначала выбери проект через /project Название_проекта")
        return

    project = data_store[user_id]["current_project"]
    warmup = (
        "🔥 Прогрев для подписчиков:\n"
        "1. Поделиться личной болью\n"
        "2. Рассказать, что ты ищешь решение\n"
        "3. Спросить мнение аудитории\n"
        "4. Подвести к будущему посту/Reels"
    )
    data_store[user_id][project]["warmups"].append(warmup)
    bot.reply_to(message, warmup)

# Генерация постов, Reels, сторис
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    if user_id not in data_store or "current_project" not in data_store[user_id]:
        bot.reply_to(message, "❌ Сначала выбери проект через /project Название_проекта")
        return

    project = data_store[user_id]["current_project"]
    text = message.text.lower()
    response = ""

    if "пост" in text:
        response = "✍️ Шаблон поста:\n1. Крючок\n2. История/боль\n3. Решение\n4. Призыв к действию"
        data_store[user_id][project]["posts"].append(response)
    elif "reels" in text:
        response = "🎬 Пример сценария Reels:\n1. Вступление — боль\n2. Поворот\n3. Короткое решение\n4. Концовка"
        data_store[user_id][project]["reels"].append(response)
    elif "сторис" in text:
        response = "📱 Идея для сторис:\n— Вопрос аудитории\n— Ваш честный ответ\n— Визуальный акцент"
        data_store[user_id][project]["stories"].append(response)
    else:
        response = "Я пока учусь 😉 Скажи: пост, reels, сторис, /plan или /warmup?"

    bot.reply_to(message, response)

bot.polling(none_stop=True)
