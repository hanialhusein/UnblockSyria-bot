import telebot
import logging
import os
from dotenv import load_dotenv
from Commands import start, search
from Callbacks import browse, service

load_dotenv()

bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Commands
@bot.message_handler(commands=['start'])
def handle_start(message):
    param = message.text.split(' ', 1)[1].strip() if ' ' in message.text else ''
    if param.startswith('service_'):
        slug = param.replace('service_', '')
        service.send_service_card(message, slug, bot)
    else:
        start.send_welcome(message, bot)

@bot.message_handler(commands=['search'])
def handle_search(message):
    search.handle_search(message, bot)

@bot.message_handler(commands=['browse'])
def handle_browse_command(message):
    keyboard = telebot.types.InlineKeyboardMarkup([[
        telebot.types.InlineKeyboardButton("📋 Browse Services", callback_data="browse_page_0")
    ]])
    bot.send_message(message.chat.id, "Select a service:", reply_markup=keyboard)

# Inline search
@bot.inline_handler(func=lambda query: True)
def handle_inline(query):
    search.handle_inline(query, bot)

# Callbacks
@bot.callback_query_handler(func=lambda call: call.data == 'home')
def handle_home(call):
    start.send_welcome(call, bot)

@bot.callback_query_handler(func=lambda call: call.data == 'noop')
def handle_noop(call):
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('browse_page_'))
def handle_browse(call):
    browse.handle_browse(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('service_'))
def handle_service(call):
    service.handle_service(call, bot)

@bot.callback_query_handler(func=lambda call: call.data.startswith('email_'))
def handle_email(call):
    service.handle_email(call, bot)

logging.info("Bot is running...")

try:
    bot.infinity_polling()
except KeyboardInterrupt:
    logging.info("Bot stopped.")
