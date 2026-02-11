import os 
import asyncio 
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup 
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes 
from telegram.request import HTTPXRequest 
from dotenv import load_dotenv 
from flask import Flask, request 
 
load_dotenv() 
TOKEN = os.getenv("TELEGRAM_TOKEN") 
WEBHOOK_URL = os.getenv("WEBHOOK_URL", "") 
PORT = int(os.environ.get("PORT", 5000)) 
 
# Create Flask app 
app = Flask(__name__) 
 
# Create Telegram application with timeout settings 
request_obj = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0, write_timeout=30.0) 
telegram_app = Application.builder().token(TOKEN).request(request_obj).build() 
 
# ============= HANDLERS ============= 
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    keyboard = [[KeyboardButton("?? Share Farm Location", request_location=True)]] 
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) 
    welcome_text = f"?? Welcome {update.effective_user.first_name}!\n\nMeghdoot Weather Advisor\nYour AI farming companion\n\nShare your location to get started!" 
    await update.message.reply_text(welcome_text, reply_markup=reply_markup) 
 
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    loc = update.message.location 
    lat, lon = loc.latitude, loc.longitude 
    response = f"? Location Received!\n\n?? Latitude: {lat:.4f}\n?? Longitude: {lon:.4f}\n\n??? Weather data coming soon!" 
    await update.message.reply_text(response) 
 
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    help_text = "?? Meghdoot Help\n\n/start - Start the bot\n/help - Show this help\n\nShare your location for weather forecasts!" 
    await update.message.reply_text(help_text) 
 
# Add handlers 
telegram_app.add_handler(CommandHandler("start", start)) 
telegram_app.add_handler(CommandHandler("help", help_command)) 
telegram_app.add_handler(MessageHandler(filters.LOCATION, handle_location)) 
 
# ============= FLASK WEBHOOK ROUTES ============= 
@app.route('/') 
def home(): 
    return "?? Meghdoot Weather Bot is running!" 
 
@app.route('/health') 
def health(): 
    return "? Healthy" 
 
@app.route(f'/{TOKEN}', methods=['POST']) 
async def webhook(): 
    update = Update.de_json(request.get_json(), telegram_app.bot) 
    await telegram_app.process_update(update) 
    return "OK" 
 
@app.route('/set_webhook', methods=['GET']) 
def set_webhook(): 
    if WEBHOOK_URL: 
        webhook_url = f"{WEBHOOK_URL}/{TOKEN}" 
        success = asyncio.run(telegram_app.bot.set_webhook(url=webhook_url)) 
        if success: 
            return f"? Webhook set to: {webhook_url}" 
    return "? WEBHOOK_URL not configured" 
 
# ============= INITIALIZATION ============= 
async def init(): 
    await telegram_app.initialize() 
    print("? Meghdoot bot initialized") 
    if WEBHOOK_URL: 
        webhook_url = f"{WEBHOOK_URL}/{TOKEN}" 
        await telegram_app.bot.set_webhook(url=webhook_url) 
        print(f"? Webhook set: {webhook_url}") 
 
if __name__ == "__main__": 
    asyncio.run(init()) 
    print(f"?? Flask server starting on port {PORT}") 
    app.run(host="0.0.0.0", port=PORT) 
