from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import os

def load_services():
    path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'services.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def send_welcome(event, bot):
    from telebot import types

    if isinstance(event, types.Message):
        chat_id = event.chat.id
        message_id = None
    elif isinstance(event, types.CallbackQuery):
        chat_id = event.message.chat.id
        message_id = event.message.message_id

    services = load_services()
    total = len(services)
    blocked = sum(1 for s in services if s.get("status") == "Blocked")
    open_ = sum(1 for s in services if s.get("status") == "Open")
    limited = sum(1 for s in services if s.get("status") in ("Limited", "Restricted"))

    text = (
        "🇸🇾 <b>Unblock Syria Bot</b>\n\n"
        "Syria's sanctions have been lifted — but many companies still block access.\n"
        "This bot helps you send formal emails to change that.\n\n"
        f"📊 <b>Current Tracker:</b>\n"
        f"🔴 Blocked: <b>{blocked}</b>   🟡 Limited: <b>{limited}</b>   🟢 Open: <b>{open_}</b>\n"
        f"<i>{total} services tracked</i>\n\n"
        "Browse services below or tap 🔍 to search inline:"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Browse Services", callback_data="browse_page_0")],
        [InlineKeyboardButton("🔍 Search a Service", switch_inline_query_current_chat=" ")],
    ])

    if message_id:
        bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML', reply_markup=keyboard)
    else:
        bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=keyboard)
