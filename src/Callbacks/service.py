import json
import os
import re
import requests
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BASE_URL = "https://unblocksyria.com/en/services/"

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

def get_service_by_slug(slug):
    return next((s for s in load_services() if s['slug'] == slug), None)

def fetch_contact_email(slug):
    try:
        url = BASE_URL + slug
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code != 200:
            return None

        emails = re.findall(r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', resp.text)

        skip = {'corporateaffairs@unblocksyria.com', 'hello@unblocksyria.com', 'noreply@unblocksyria.com'}
        filtered = [
            e for e in emails
            if e.lower() not in skip
            and 'unblocksyria' not in e.lower()
            and not e.endswith(('.png', '.svg', '.jpg'))
        ]

        seen = set()
        unique = []
        for e in filtered:
            if e.lower() not in seen:
                seen.add(e.lower())
                unique.append(e)

        return unique[0] if unique else None
    except Exception:
        return None

def generate_email(service, contact_email):
    name = service['name']
    # derive company name from slug if needed
    company = ' '.join(w.capitalize() for w in service['slug'].split('-'))
    email_to = contact_email or f"support@{service['slug'].replace('-', '')}.com"

    return (
        f"To: {email_to}\n"
        f"CC: corporateaffairs@unblocksyria.com\n"
        f"Subject: Request to Enable Service Access in Syria\n\n"
        f"Dear {company} Team,\n\n"
        f"I am writing to request that {name} access be enabled for users in Syria.\n\n"
        f"Following the lifting of the comprehensive trade embargo on Syria announced by the U.S. Treasury "
        f"in December 2025, all sanctions on Syria have now been lifted by both the United States and the "
        f"European Union. Syria is no longer listed under OFAC's embargoed countries.\n\n"
        f"For reference:\n"
        f"1- U.S. Treasury announcement: https://ofac.treasury.gov/media/934736/download?inline\n"
        f"2- OFAC sanctions programs overview: https://ofac.treasury.gov/sanctions-programs-and-country-information\n\n"
        f"Supporting documentation is also available at: https://unblocksyria.com/resources\n\n"
        f"Several other companies have already enabled access for Syria. As millions of Syrians work to "
        f"rebuild their country, access to global digital services is increasingly important.\n\n"
        f"I kindly request a review of the current restriction and would appreciate confirmation on whether "
        f"Syria can now be onboarded and supported on your platform.\n\n"
        f"Best regards"
    )

def handle_service(call, bot):
    slug = call.data.replace("service_", "")
    service = get_service_by_slug(slug)

    if not service:
        bot.answer_callback_query(call.id, "Service not found.")
        return

    status = service.get("status", "Unknown")
    status_emoji = STATUS_EMOJI.get(status, "⚪")
    tags = service.get("tags", [])
    tag_str = "  ".join(f"{TAG_EMOJI.get(t, '🏷️')} {t}" for t in tags) if tags else "—"
    desc = service.get("description", "")

    text = (
        f"{status_emoji} <b>{service['name']}</b>\n"
        f"Status: <b>{status}</b>\n"
        f"Progress: {tag_str}\n"
    )
    if desc:
        text += f"\n<i>{desc}</i>\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Get Email Template", callback_data=f"email_{slug}")],
        [InlineKeyboardButton("🌐 View on UnblockSyria", url=f"https://unblocksyria.com/en/services/{slug}")],
        [InlineKeyboardButton("⬅️ Back to List", callback_data="browse_page_0"),
         InlineKeyboardButton("🏠 Home", callback_data="home")],
    ])

    bot.edit_message_text(
        text,
        call.message.chat.id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=keyboard
    )

def handle_email(call, bot):
    slug = call.data.replace("email_", "")
    service = get_service_by_slug(slug)

    if not service:
        bot.answer_callback_query(call.id, "Service not found.")
        return

    bot.answer_callback_query(call.id, "⏳ Fetching contact info...")

    contact_email = fetch_contact_email(slug)
    email_text = generate_email(service, contact_email)

    if contact_email:
        email_note = f"📬 Found contact: <code>{contact_email}</code>"
    else:
        email_note = "⚠️ No contact email found — using generic address. Check their site to verify."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("⬅️ Back", callback_data=f"service_{slug}"),
         InlineKeyboardButton("🏠 Home", callback_data="home")],
    ])

    bot.send_message(
        call.message.chat.id,
        f"📧 <b>Email for {service['name']}</b>\n"
        f"{email_note}\n\n"
        f"Copy and send this email:\n\n"
        f"<code>{email_text}</code>",
        parse_mode='HTML',
        reply_markup=keyboard
    )

def send_service_card(message, slug, bot):
    """Used by deep links: /start service_<slug>"""
    service = get_service_by_slug(slug)

    if not service:
        bot.send_message(message.chat.id, "❌ Service not found.")
        return

    status = service.get("status", "Unknown")
    status_emoji = STATUS_EMOJI.get(status, "⚪")
    tags = service.get("tags", [])
    tag_str = "  ".join(f"{TAG_EMOJI.get(t, '🏷️')} {t}" for t in tags) if tags else "—"
    desc = service.get("description", "")

    text = (
        f"{status_emoji} <b>{service['name']}</b>\n"
        f"Status: <b>{status}</b>\n"
        f"Progress: {tag_str}\n"
    )
    if desc:
        text += f"\n<i>{desc}</i>\n"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📧 Get Email Template", callback_data=f"email_{slug}")],
        [InlineKeyboardButton("🌐 View on UnblockSyria", url=f"https://unblocksyria.com/en/services/{slug}")],
        [InlineKeyboardButton("📋 Browse All", callback_data="browse_page_0"),
         InlineKeyboardButton("🏠 Home", callback_data="home")],
    ])

    bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=keyboard)
