import telebot
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

keyboard = telebot.types.ReplyKeyboardMarkup()

button_limited = False

stages = {}

def print_user(message):
    print(f'{message.from_user.id}|{message.from_user.username}: {message.text}')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print_user(message)
    bot.send_message(message.chat.id, "Hello. I'm a bot that can create your personal dictionary. Enter `/newDictionary' for to create new dictionary ")

@bot.message_handler(commands=['newDictionary'])
def buttons(message):
    print_user(message)
    stages[message.chat.id] = 'waiting_for_name'
    user_id = message.from_user.id
    global button_limited
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    add_button = telebot.types.KeyboardButton('Add word')
    edit_button = telebot.types.KeyboardButton('Edit word')
    all_word_button = telebot.types.KeyboardButton('All words')
    remove_buttons = telebot.types.KeyboardButton('Remove word')
    
    keyboard.add(add_button, edit_button, all_word_button, remove_buttons)
    
    with sqlite3.connect(f'db/{user_id}.db') as file_db:
        cursor = file_db.cursor()
        request = f"""CREATE TABLE IF NOT EXISTS {user_id} (
            id INTEGER PRIMARY KEY, 
            word TEXT,
            meaning TEXT
            );"""
        cursor.execute(request)
    bot.send_message(user_id, 'Congratulation! Your new dictionary was create. Enter ')
    
    button_limited = False

bot.infinity_polling()