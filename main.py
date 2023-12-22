import telebot
import os
from dotenv import load_dotenv
import sqlite3

load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)

buttons_limited = True
is_word = None
current_word = None

states = {}

def keyboard_call():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    add_button = telebot.types.KeyboardButton('Add new word')
    edit_button = telebot.types.KeyboardButton('Edit word')
    search_word_button = telebot.types.KeyboardButton('Search word')
    remove_buttons = telebot.types.KeyboardButton('Remove word')
    
    keyboard.add(add_button, edit_button, search_word_button, remove_buttons)
    return keyboard

def print_user(message):
    print(f'{message.from_user.id}|{message.from_user.username}: {message.text}')

@bot.message_handler(commands=['start'])
def send_welcome(message):
    print_user(message)
    bot.send_message(message.chat.id, "Hello. I'm a bot that can create your personal dictionary. Enter /newDictionary for to create new dictionary ")

@bot.message_handler(commands=['newDictionary'])
def buttons(message):
    print_user(message)
    user_id = message.from_user.id
    global buttons_limited
    
    with sqlite3.connect('db/dictionary.db') as file_db:
        cursor = file_db.cursor()
        request = f"""CREATE TABLE IF NOT EXISTS '{user_id}' (
            id INTEGER PRIMARY KEY, 
            word TEXT,
            meaning TEXT
            );"""
        cursor.execute(request)
    bot.send_message(user_id, 'Congratulation! Your new dictionary was create. \nChoose button: \n\n' +
                     '*Add new word* - _add a new word to your dictionary_.\n\n' +
                     '*Edit word* - _edit a word in your dictionary_.\n\n' +
                     '*Search word* - _search a word in your dictionary_.\n\n' +
                     '*Remove word* - _remove a word from your dictionary_.\n\n', parse_mode='Markdown', reply_markup=keyboard_call())
    buttons_limited = False

@bot.message_handler(func=lambda message: ('Add new word' in message.text or 'Edit word' in message.text or 'Search word' in message.text or 'Remove word' in message.text))
def button_handler(message):
    global buttons_limited
    global is_word
    user_id = message.from_user.id
    keyboard = telebot.types.ReplyKeyboardRemove()
    print_user(message)
    if buttons_limited == False:
        print_user(message)
        if message.text == 'Add new word':
            is_word = True
            buttons_limited = True
            states[user_id] = 'add_new_word'
            
            bot.send_message(user_id, 'Send me your new word:', reply_markup=keyboard)
        elif message.text == 'Search word':
            buttons_limited = True
            states[user_id] = 'search_word'
            
            bot.send_message(user_id, 'What word do you want to find?', reply_markup=keyboard)
        elif message.text == 'Remove word':
            buttons_limited = True
            states[user_id] = 'remove_word'
            
            bot.send_message(user_id, 'Send me the word you want to delete.', reply_markup=keyboard)

@bot.message_handler(func=lambda message: states.get(message.from_user.id) == 'add_new_word')
def add_new_word(message):
    global is_word
    global current_word
    global buttons_limited
    user_id = message.from_user.id
    keyboard = keyboard_call()
    
    if is_word == True:
        print_user(message)
        
        with sqlite3.connect('db/dictionary.db') as file_db:
            cursor = file_db.cursor()
            request = f"""INSERT INTO '{user_id}' (word) VALUES ('{message.text}');"""
            cursor.execute(request)
        bot.send_message(user_id, 'Send me meaning for your word: ')
        current_word = message.text
        is_word = False
    elif is_word == False and current_word is not None:
        print_user(message)
        
        with sqlite3.connect('db/dictionary.db') as file_db:
            cursor = file_db.cursor()
            request = f"""UPDATE '{user_id}' SET meaning = '{message.text}'  WHERE word = '{current_word}';"""
            cursor.execute(request)
        current_word = None
        buttons_limited = False
        states.pop(user_id)
        bot.send_message(user_id, 'Congratulations! Your word has been added to your dictionary.', reply_markup=keyboard)

@bot.message_handler(func=lambda message: states.get(message.from_user.id) == 'search_word')
def search_word(message):
    global buttons_limited
    user_id = message.from_user.id
    keyboard = keyboard_call()
    
    print_user(message)
    try:
        with sqlite3.connect('db/dictionary.db') as file_db:
            cursor = file_db.cursor()
            request = f"""SELECT word, meaning FROM '{user_id}' WHERE word = '{message.text}';"""
            cursor.execute(request)
        output = cursor.fetchone()
        buttons_limited = False
        states.pop(user_id)
        
        bot.send_message(user_id, f'*{output[0]}* - _{output[1]}_.', parse_mode='Markdown', reply_markup=keyboard)
    except:
        bot.send_message(user_id, 'Word os not found!', reply_markup=keyboard)

@bot.message_handler(func=lambda message: states.get(message.from_user.id) == 'remove_word')
def remove_word(message):
    global buttons_limited
    user_id = message.from_user.id
    keyboard = keyboard_call()
    
    print_user(message)
    with sqlite3.connect('db/dictionary.db') as file_db:
        cursor = file_db.cursor()
        request = f"""DELETE FROM '{user_id}' WHERE word = '{message.text}';"""
        cursor.execute(request)
    buttons_limited = False
    states.pop(user_id)
    bot.send_message(user_id, 'Congratulations! This word has been removed from your dictionary.', reply_markup=keyboard)

bot.infinity_polling()