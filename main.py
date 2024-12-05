import telebot
from telebot import types
import sqlite3

bot = telebot.TeleBot('7588620170:AAGHyo0KRSincHGHP2P3KN2nWF6EENU3vCc')

def init_db():
    conn = sqlite3.connect('recipes.db')
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS recipes (id INTEGER PRIMARY KEY AUTOINCREMENT,title TEXT NOT NULL,description TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Посмотреть рецепты"))
    markup.add(types.KeyboardButton("Добавить рецепт"))
    bot.send_message(
        message.chat.id,
        'Привет! Я бот для помощи поиска рецептов для десертов.',
        reply_markup=markup
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    if message.text == "Посмотреть рецепты":
        conn = sqlite3.connect('recipes.db')
        cur = conn.cursor()
        cur.execute("SELECT id, title FROM recipes")
        recipes = cur.fetchall()
        conn.close()

        if recipes:
            markup = types.InlineKeyboardMarkup()
            for recipe_id, title in recipes:
                markup.add(
                    types.InlineKeyboardButton(title, callback_data=f"recipe_{recipe_id}")
                )
            bot.send_message(message.chat.id, "Выберите рецепт для подробного просмотра:", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Рецептов пока нет. Добавьте новый рецепт!")
    elif message.text == "Добавить рецепт":
        bot.send_message(message.chat.id, "Введите название рецепта:")
        bot.register_next_step_handler(message, add_recipe_title)

def add_recipe_title(message):
    title = message.text
    bot.send_message(message.chat.id, "Введите полный рецепт:")
    bot.register_next_step_handler(message, add_recipe_description, title)

def add_recipe_description(message, title):
    description = message.text
    conn = sqlite3.connect('recipes.db')
    cur = conn.cursor()
    cur.execute("INSERT INTO recipes (title, description) VALUES (?, ?)", (title, description))
    conn.commit()
    conn.close()
    bot.send_message(message.chat.id, f"Рецепт '{title}' добавлен!")

@bot.callback_query_handler(func=lambda call: call.data.startswith("recipe_"))
def callback_view_recipe(call):
    try:
        recipe_id = int(call.data.split("_")[1])
        conn = sqlite3.connect('recipes.db')
        cur = conn.cursor()
        cur.execute("SELECT title, description FROM recipes WHERE id = ?", (recipe_id,))
        recipe = cur.fetchone()
        conn.close()

        if recipe:
            title, description = recipe
            bot.send_message(
                call.message.chat.id,
                f"**{title}**\n\n{description}",
                parse_mode="Markdown"
            )
        else:
            bot.send_message(call.message.chat.id, "Такого рецепта не существует.")
    except Exception as e:
        print(f"Ошибка при обработке callback: {e}")
        bot.send_message(call.message.chat.id, "Произошла ошибка при отображении рецепта.")

bot.polling(non_stop=True)
