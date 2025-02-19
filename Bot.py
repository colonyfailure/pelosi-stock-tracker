import requests
import time
import json
import os
from telegram import Bot

# Load environment variables from Railway
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Quiver Quantitative API Endpoint (or use another source)
QUIVER_URL = "https://www.quiverquant.com/congresstrading/politician/Nancy%20Pelosi-P000197"

# File to track last seen trade
LAST_TRADE_FILE = "last_trade.json"

# Initialize bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def get_pelosi_trades():
    """Fetch Nancy Pelosi's latest stock trades"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(QUIVER_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to fetch data:", response.status_code)
        return None

def load_last_trade():
    """Load last recorded trade from file"""
    try:
        with open(LAST_TRADE_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_last_trade(trade):
    """Save latest trade to file"""
    with open(LAST_TRADE_FILE, "w") as file:
        json.dump(trade, file)

def check_new_trades():
    """Check for new trades and send Telegram alerts"""
    trades = get_pelosi_trades()
    
    if trades:
        last_trade = load_last_trade()
        new_trade = trades[0]  # Get the latest trade

        if new_trade != last_trade:  # Compare with last saved trade
            message = f"🚨 New Pelosi Stock Trade 🚨\n\n"
            message += f"📅 Date: {new_trade['TransactionDate']}\n"
            message += f"🏢 Company: {new_trade['Company']}\n"
            message += f"💰 Amount: {new_trade['ValueRange']}\n"
            message += f"📈 Type: {new_trade['TransactionType']}\n\n"
            message += f"🔗 More info: {QUIVER_URL}"

            # Send Telegram alert
            bot.send_message(chat_id=CHAT_ID, text=message)

            # Save latest trade
            save_last_trade(new_trade)

if __name__ == "__main__":
    while True:
        check_new_trades()
        time.sleep(3600)  # Check every hour
