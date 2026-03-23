# 🇸🇾 UnblockSyria Bot

A Telegram bot that helps Syrians send formal emails to companies that still block access to Syria — even though all sanctions have been lifted since December 2025.

Built in collaboration with [UnblockSyria.com](https://unblocksyria.com).

---

## Features

- 📋 **Browse** 780+ tracked services with their current status
- 🔍 **Search** by service name via command or inline mode
- 📧 **Generate** a ready-to-copy formal email for any blocked service
- 🔴🟡🟢 **Status indicators** — Blocked, Limited, Restricted, Open
- 🏷️ **Progress tags** — Contacted, In Review, Unblocked, Declined, etc.
- 📊 **Live stats** on the home screen
- 🌐 **Inline search** — works in any Telegram chat via `@YourBot`

---

## Project Structure

```
UnblockSyria-bot/
├── src/
│   ├── main.py                  # Entry point, bot setup, handlers
│   ├── Commands/
│   │   ├── start.py             # /start command & welcome message
│   │   └── search.py            # /search command & inline query handler
│   ├── Callbacks/
│   │   ├── browse.py            # Paginated service browser
│   │   └── service.py           # Service detail card & email generator
│   └── Data/
│       └── services.json
├── Dockerfile
├── requirements.txt
├── .env
└── .gitignore
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/youruser/UnblockSyria-bot.git
cd UnblockSyria-bot
```

### 2. Create your `.env` file

```env
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=YourBotUsername
```

- Get your token from [@BotFather](https://t.me/BotFather)
- `BOT_USERNAME` is your bot's username **without** the `@`

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the bot

```bash
python src/main.py
```

---

## Docker

```bash
docker build -t unblocksyria-bot .
docker run --env-file .env unblocksyria-bot
```

---

## Enabling Inline Search

To allow users to search via `@YourBot` in any chat:

1. Open [@BotFather](https://t.me/BotFather)
2. Send `/setinline` → select your bot
3. Set a placeholder, e.g.: `Search for a service...`

Once enabled, users can type `@YourBot paypal` in any chat to get instant results with a button that opens the full service card in private.

---

## Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome message with stats and navigation |
| `/search <name>` | Search for a service by name |
| `/browse` | Open the paginated service browser |

---

## Tech Stack

- **Python 3.11**
- **pyTelegramBotAPI** — Telegram bot framework
- **requests** — for fetching contact emails live
- **python-dotenv** — environment variable management
- **Docker** — containerized deployment

---

## License

MIT
