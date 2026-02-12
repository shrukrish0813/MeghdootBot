import os
import requests
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from flask import Flask, request
import asyncio

# ============ CONFIGURATION ============
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 5000))

# Flask app
app = Flask(__name__)

# ============ WEATHER FUNCTIONS ============
def get_weather(lat, lon):
    """Fetch weather from Open-Meteo"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m",
            "forecast_days": 3,
            "timezone": "auto"
        }
        r = requests.get(url, params=params, timeout=10)
        return r.json()
    except:
        return None

def format_weather(data, location="Your Farm"):
    """Format weather message"""
    if not data:
        return "❌ Weather data unavailable"
    
    try:
        hourly = data['hourly']
        temp = hourly['temperature_2m'][0]
        temps = hourly['temperature_2m'][:72]
        
        msg = f"🌾 *Meghdoot Weather* 🌾\n"
        msg += f"📍 {location}\n"
        msg += f"⏰ {datetime.now().strftime('%d %b %I:%M %p')}\n\n"
        msg += f"*🌡️ Current:* {temp:.1f}°C\n\n"
        msg += f"*📅 3-Day Forecast:*\n"
        
        for day in range(3):
            start = day * 24
            day_temps = temps[start:start+24]
            day_min = min(day_temps)
            day_max = max(day_temps)
            date = datetime.fromisoformat(hourly['time'][start].replace('Z', '+00:00'))
            msg += f"• {date.strftime('%a')}: {day_min:.0f}-{day_max:.0f}°C\n"
        
        msg += f"\n*💡 Advice:*\n"
        if temp > 35:
            msg += "• 🔥 Heat stress - irrigate\n"
        elif temp < 10:
            msg += "• ❄️ Frost risk - protect crops\n"
        else:
            msg += "• 🌱 Normal conditions\n"
        msg += "• 💧 Water in early morning\n"
        
        return msg
    except:
        return "❌ Error processing weather"

# ============ BOT HANDLERS ============
async def start(update, context):
    """Start command"""
    keyboard = [[KeyboardButton("📍 Share Location", request_location=True)]]
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🌾 *Meghdoot Weather Bot*\n\nShare your location for forecast ⬇️",
        parse_mode='Markdown',
        reply_markup=reply
    )

async def location(update, context):
    """Location handler"""
    loc = update.message.location
    lat, lon = loc.latitude, loc.longitude
    
    await update.message.chat.send_action(action="typing")
    weather = get_weather(lat, lon)
    
    if weather:
        msg = format_weather(weather, f"{lat:.2f}, {lon:.2f}")
        await update.message.reply_text(msg, parse_mode='Markdown')
    else:
        await update.message.reply_text("❌ Weather fetch failed")

# ============ CREATE APPLICATION - NO POLLING! ============
bot_app = Application.builder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.LOCATION, location))

# ============ FLASK WEBHOOK ============
@app.route('/')
def home():
    return "🌾 Meghdoot Bot Online! ✅"

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    """Telegram webhook"""
    update = Update.de_json(request.get_json(), bot_app.bot)
    await bot_app.process_update(update)
    return "OK"

# ============ INIT ============
async def init():
    """Initialize bot"""
    await bot_app.initialize()
    railway_url = os.environ.get('RAILWAY_STATIC_URL')
    if railway_url:
        webhook_url = f"https://{railway_url}/{TOKEN}"
        await bot_app.bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook: {webhook_url}")

# ============ MAIN ============
if __name__ == "__main__":
    asyncio.run(init())
    print(f"🚀 Server on 0.0.0.0:{PORT}")
    app.run(host="0.0.0.0", port=PORT)