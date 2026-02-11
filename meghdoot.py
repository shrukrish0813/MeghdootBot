import os 
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
from telegram.request import HTTPXRequest 
from dotenv import load_dotenv 
 
load_dotenv() 
TOKEN = os.getenv("TELEGRAM_TOKEN") 
 
async def start(update, context): 
    keyboard = [[KeyboardButton("Share Location", request_location=True)]] 
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("Welcome to Meghdoot! Share location.", reply_markup=reply_markup) 
 
async def handle_location(update, context): 
    loc = update.message.location 
    response = f"Location: {loc.latitude:.4f}, {loc.longitude:.4f}" 
    await update.message.reply_text(response) 
 
def main(): 
    print("Starting Meghdoot Bot...") 
 
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0, write_timeout=30.0) 
 
    app = Application.builder().token(TOKEN).request(request).build() 
 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(MessageHandler(filters.LOCATION, handle_location)) 
 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
