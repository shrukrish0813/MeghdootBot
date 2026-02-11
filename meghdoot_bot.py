import os 
import asyncio 
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
from dotenv import load_dotenv 
 
load_dotenv() 
TOKEN = os.getenv("TELEGRAM_TOKEN") 
 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    keyboard = [[KeyboardButton("?? Share Location", request_location=True)]] 
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    await update.message.reply_text("?? Meghdoot Bot is working!", reply_markup=reply_markup) 
 
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    loc = update.message.location 
    await update.message.reply_text(f"? Location received!\nLat: {loc.latitude:.4f}\nLon: {loc.longitude:.4f}") 
 
def main(): 
    print("=" * 50) 
    print("?? MEGHDOOT BOT STARTING...") 
    print("=" * 50) 
 
    app = Application.builder().token(TOKEN).build() 
    app.add_handler(CommandHandler("start", start)) 
    app.add_handler(MessageHandler(filters.LOCATION, handle_location)) 
 
    print("? Bot is running! Press Ctrl+C to stop.") 
    app.run_polling() 
 
if __name__ == "__main__": 
    main() 
