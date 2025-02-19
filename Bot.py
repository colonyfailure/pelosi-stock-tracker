import requests
import time
import json
import os
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext

# Load environment variables from Railway
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Quiver Quantitative API Endpoint (or another source)
QUIVER_URL = "https://www.quiverquant.com/congresstrading/politician/Nancy%20Pelosi-P000197"

# File to store user subscriptions
SUBSCRIBERS_FILE = "subscribers.json"

# Initialize bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def load_subscribers():
    """Load subscribed user chat IDs from file"""
    try:
        with open(SUBSCRIBERS_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_subscribers(subscribers):
    """Save subscribed user chat IDs to file"""
    with open(SUBSCRIBERS_FILE, "w") as file:
        json.dump(subscribers, file)

def start(update: Update, context: CallbackContext):
    """Handles /start command"""
    chat_id = update.message.chat_id
    subscribers = load_subscribers()

    if chat_id not in subscribers:
        subscribers.append(chat_id)
        save_subscribers(subscribers)
        update.message.reply_text("✅ You have subscribed to Nancy Pelosi stock alerts!")
    else:
        update.message.reply_text("ℹ️ You are already subscribed!")

def stop(update: Update, context: CallbackContext):
    """Handles /stop command"""
    chat_id = update.message.chat_id
    subscribers = load_subscribers()

    if chat_id in subscribers:
        subscribers.remove(chat_id)
        save_subscribers(subscribers)
        update.message.reply_text("❌ You have unsubscribed from stock alerts.")
    else:
        update.message.reply_text("ℹ️ You are not subscribed.")

def get_pelosi_trades():
    """Fetch Nancy Pelosi's latest stock trades"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(QUIVER_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data:", response.status_code)
        return None

def check_new_trades():
    """Check for new trades and send Telegram alerts"""
    trades = get_pelosi_trades()
    
    if trades:
        last_trade = trades[0]  # Get the latest trade
        subscribers = load_subscribers()

        if subscribers:
            message = f"🚨 New Pelosi Stock Trade 🚨\n\n"
            message += f"📅 Date: {last_trade['TransactionDate']}\n"
            message += f"🏢 Company: {last_trade['Company']}\n"
            message += f"💰 Amount: {last_trade['ValueRange']}\n"
            message += f"📈 Type: {last_trade['TransactionType']}\n\n"
            message += f"🔗 More info: {QUIVER_URL}"

            # Send message to all subscribers
            for chat_id in subscribers:
                bot.send_message(chat_id=chat_id, text=message)

# Set up Telegram commands
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("stop", stop))

    updater.start_polling()
    
    while True:
        check_new_trades()
        time.sleep(3600)  # Check every hour

if __name__ == "__main__":
    main()
