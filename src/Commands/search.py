import json
import os
import uuid
from dotenv import load_dotenv
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    InlineQueryResultArticle, InputTextMessageContent
)

load_dotenv()

BOT_USERNAME = os.getenv("BOT_USERNAME")  # set this in your .env

STATUS_EMOJI = {
    "Blocked": "🔴",
    "Limited": "🟡",
    "Restricted": "🟠",
    "Open": "🟢",
    "Unknown": "⚪",
}

TAG_EMOJI = {
    "Contacted": "📨",
    "In Review": "🔍",
    "Unblocked": "✅",
    "Partially Resolved": "🔄",
    "Declined": "❌",
}

def load_services():
    path = os.path.join(os.path.dirname(__file__), '..', 'Data', 'services.json')
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def handle_search(message, bot):
    query = message.text.replace('/search', '').strip()

    if not query:
        bot.send_message(
            message.chat.id,
            "🔍 Send a service name to search.\nExample: <code>/search PayPal</code>\n\n"
            "Or tap the button below to search inline from any chat:",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔍 Search Inline", switch_inline_query_current_chat="")]
            ])
        )
        return

    services = load_services()
    query_lower = query.lower()
    results = [
        s for s in services
        if query_lower in s['name'].lower() or query_lower in s['slug'].replace('-', ' ')
    ]

    if not results:
        bot.send_message(
            message.chat.id,
            f"❌ No results for <b>{query}</b>.\n\nTry browsing all services:",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📋 Browse Services", callback_data="browse_page_0")]
            ])
        )
        return

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(
            f"{STATUS_EMOJI.get(s.get('status', ''), '⚪')} {s['name']}",
            callback_data=f"service_{s['slug']}"
        )]
        for s in results[:10]
    ])

    bot.send_message(
        message.chat.id,
        f"🔍 <b>{len(results)} result(s)</b> for <b>{query}</b>"
        + (" — showing top 10" if len(results) > 10 else "") + ":",
        parse_mode='HTML',
        reply_markup=keyboard
    )

def handle_inline(query, bot):
    q = query.query.strip().lower()
    services = load_services()

    if q:
        matches = [
            s for s in services
            if q in s['name'].lower() or q in s['slug'].replace('-', ' ')
        ]
    else:
        matches = sorted(services, key=lambda s: s.get('status', '') != 'Blocked')

    results = []
    for s in matches[:20]:
        status = s.get('status', 'Unknown')
        emoji = STATUS_EMOJI.get(status, '⚪')
        tags = s.get('tags', [])
        tag_str = '  '.join(f"{TAG_EMOJI.get(t, '🏷️')} {t}" for t in tags) if tags else '—'
        desc = s.get('description', '')

        results.append(InlineQueryResultArticle(
            id=str(uuid.uuid4()),
            title=f"{emoji} {s['name']}",
            description=f"{status}  {tag_str}\n{desc}",
            input_message_content=InputTextMessageContent(
                f"{emoji} <b>{s['name']}</b> — {status}\n\n"
                f"<i>{desc}</i>",
                parse_mode='HTML'
            ),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "📋 View Details & Get Email",
                    url=f"https://t.me/{BOT_USERNAME}?start=service_{s['slug']}"
                )]
            ])
        ))

    bot.answer_inline_query(query.id, results, cache_time=30)
