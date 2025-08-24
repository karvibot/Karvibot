import telebot
import os
import openai

# --- Загрузка токенов из Environment Variables ---
API_TOKEN = os.environ.get("API_TOKEN")      # Telegram Bot Token
OPENAI_KEY = os.environ.get("OPENAI_KEY")    # OpenAI GPT Key

if not API_TOKEN or not OPENAI_KEY:
    raise ValueError("API_TOKEN или OPENAI_KEY не найдены! Проверь Environment Variables.")

bot = telebot.TeleBot(API_TOKEN)
openai.api_key = OPENAI_KEY

# --- Хранилище данных пользователей и проектов ---
data_store = {}

# --- Приветствие / помощь ---
help_text = """
Привет! 👋 Я твой контент-бот.

Просто пиши мне:
- "Сделай пост про тему X"
- "Составь Reels на тему Y"
- "Придумай сторис на тему Z"
- "Создай контент-план на неделю для проекта X"
- "Придумай прогрев для проекта X"

Я сохраню всё и смогу выдавать по проектам.
"""

@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.reply_to(message, help_text)

# --- Выбор/создание проекта ---
@bot.message_handler(commands=['project'])
def select_project(message):
    text_parts = message.text.split(maxsplit=1)
    if len(text_parts) < 2 or not text_parts[1].strip():
        bot.reply_to(message, "❌ Укажи название проекта после команды /project")
        return

    project_name = text_parts[1].strip()
    user_id = str(message.from_user.id)

    if user_id not in data_store:
        data_store[user_id] = {}

    if project_name not in data_store[user_id]:
        data_store[user_id][project_name] = {
            "posts": [], "reels": [], "stories": [], "plans": [], "warmups": []
        }

    data_store[user_id]["current_project"] = project_name
    bot.reply_to(message, f"✅ Выбран проект: {project_name}\nТеперь можешь писать запросы на контент.")

# --- Показать сохранённый контент ---
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

# --- Основная генерация контента через GPT ---
def generate_gpt(prompt):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"❌ Ошибка GPT: {e}"

# --- Обработка всех сообщений ---
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = str(message.from_user.id)
    if user_id not in data_store or "current_project" not in data_store[user_id]:
        bot.reply_to(message, "❌ Сначала выбери проект через /project Название_проекта")
        return

    project = data_store[user_id]["current_project"]
    text = message.text.strip()

    # --- Определяем тип запроса по ключевым словам ---
    if "пост" in text.lower():
        prompt = f"Сделай текст поста для Instagram: {text}"
        result = generate_gpt(prompt)
        data_store[user_id][project]["posts"].append(result)
    elif "reels" in text.lower():
        prompt = f"Придумай сценарий Reels: {text}"
        result = generate_gpt(prompt)
        data_store[user_id][project]["reels"].append(result)
    elif "сторис" in text.lower():
        prompt = f"Придумай идею для сторис: {text}"
        result = generate_gpt(prompt)
        data_store[user_id][project]["stories"].append(result)
    elif "контент-план" in text.lower() or "plan" in text.lower():
        prompt = f"Составь контент-план на неделю для проекта {project}"
        result = generate_gpt(prompt)
        data_store[user_id][project]["plans"].append(result)
    elif "прогрев" in text.lower() or "warmup" in text.lower():
        prompt = f"Придумай прогрев для подписчиков проекта {project}"
        result = generate_gpt(prompt)
        data_store[user_id][project]["warmups"].append(result)
    else:
        # Если не поняли точно, спросим у GPT что делать
        prompt = f"Ты контент-бот. Пользователь написал: {text}. Создай пост, Reels, сторис, контент-план или прогрев, что лучше подходит."
        result = generate_gpt(prompt)
        data_store[user_id][project]["posts"].append(result)

    bot.reply_to(message, result)

# --- Запуск бота ---
bot.polling(none_stop=True)
