import json
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

PAGE_SIZE = 8

STATUS_EMOJI = {
    "Blocked": "🔴",
    "Limited": "🟡",
    "Restricted": "🟠",
    "Open": "🟢",
    "Unknown": "⚪",
}

def load_services():
    path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'services.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def handle_browse(call, bot):
    parts = call.data.split("_")
    page = int(parts[-1])
    filter_status = parts[2] if len(parts) > 3 else None  # browse_page_0 or browse_filter_Blocked_0

    services = load_services()

    if filter_status:
        services = [s for s in services if s.get("status") == filter_status]

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    page_services = services[start:end]
    total_pages = max(1, (len(services) + PAGE_SIZE - 1) // PAGE_SIZE)

    rows = []
    for s in page_services:
        emoji = STATUS_EMOJI.get(s.get("status", ""), "⚪")
        label = f"{emoji} {s['name']}"
        rows.append([InlineKeyboardButton(label, callback_data=f"service_{s['slug']}")])

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"browse_page_{page - 1}"))
    nav.append(InlineKeyboardButton(f"{page + 1}/{total_pages}", callback_data="noop"))
    if page < total_pages - 1:
        nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"browse_page_{page + 1}"))
    rows.append(nav)

    rows.append([InlineKeyboardButton("🏠 Home", callback_data="home")])

    keyboard = InlineKeyboardMarkup(rows)

    status_counts = {}
    all_services = load_services()
    for s in all_services:
        st = s.get("status", "Unknown")
        status_counts[st] = status_counts.get(st, 0) + 1

    legend = "  ".join(f"{STATUS_EMOJI.get(k,'⚪')} {k}: {v}" for k, v in sorted(status_counts.items()))

    bot.edit_message_text(
        f"📋 <b>Service Directory</b> — Page {page + 1}/{total_pages}\n"
        f"<i>{len(all_services)} services total</i>\n\n"
        f"{legend}\n\n"
        f"Select a service to get the contact email:",
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=keyboard
    )
