import os
import requests
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from flask import Flask, request
import asyncio

# ============ CONFIGURATION ============
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.environ.get("PORT", 5000))

# Flask app for webhook
app = Flask(__name__)

# Telegram application
telegram_app = Application.builder().token(TOKEN).build()

# ============ WEATHER FUNCTIONS ============
def get_weather_forecast(lat, lon):
    """Fetch weather data from Open-Meteo API (completely free, no API key)"""
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m",
            "forecast_days": 7,
            "timezone": "auto"
        }
        print(f"🌤️ Fetching weather for: {lat}, {lon}")
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def format_weather_message(weather_data, location_name="Your Farm"):
    """Format weather data for farmers"""
    if not weather_data:
        return "❌ Unable to fetch weather data."

    try:
        hourly = weather_data.get('hourly', {})
        times = hourly.get('time', [])
        temps = hourly.get('temperature_2m', [])
        
        if not times or not temps:
            return "❌ Incomplete weather data received."
        
        current_temp = temps[0]
        
        # Calculate daily min/max for next 3 days
        today_forecast = []
        for day in range(3):
            start_idx = day * 24
            end_idx = start_idx + 24
            if end_idx <= len(temps):
                day_temps = temps[start_idx:end_idx]
                day_min = min(day_temps)
                day_max = max(day_temps)
                day_date = datetime.fromisoformat(times[start_idx].replace('Z', '+00:00'))
                today_forecast.append({
                    'date': day_date,
                    'min': day_min,
                    'max': day_max
                })
        
        # Build message
        message = f"🌾 *Meghdoot Weather Advisory* 🌾\n"
        message += f"📍 *Location:* {location_name}\n"
        message += f"⏰ *Time:* {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n\n"
        message += f"*🌡️ CURRENT CONDITIONS:*\n"
        message += f"• Temperature: {current_temp:.1f}°C\n\n"
        message += f"*📅 3-DAY FORECAST:*\n"
        
        for i, day in enumerate(today_forecast[:3]):
            day_name = day['date'].strftime('%a')
            day_date = day['date'].strftime('%d %b')
            message += f"• {day_name}, {day_date}: {day['min']:.0f}-{day['max']:.0f}°C\n"
        
        message += f"\n*⚠️ FARMING RECOMMENDATIONS:*\n"
        
        if current_temp > 35:
            message += "• 🔥 Heat stress risk - irrigate early morning\n"
        elif current_temp > 32:
            message += "• ☀️ High temperature - ensure adequate irrigation\n"
        elif current_temp < 10:
            message += "• ❄️ Frost risk - protect sensitive crops\n"
        else:
            message += "• 🌡️ Normal temperature range - regular farming activities\n"
        
        message += "• 🌱 Inspect crops regularly for pests\n"
        message += "• 💧 Water plants in early morning\n"
        message += "• 📋 Plan harvesting around weather\n"
        message += f"\n_Data: Open-Meteo | Free Weather API_ ☁️"
        
        return message
    except Exception as e:
        print(f"Format error: {e}")
        return "❌ Error processing weather data."

# ============ TELEGRAM HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    keyboard = [[KeyboardButton("📍 Share Farm Location", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "🌾 *Welcome to Meghdoot Weather Bot!* 🌾\n\n"
        "Your AI-powered farming companion.\n\n"
        "👇 *Share your location to get hyperlocal weather forecast*",
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle location sharing"""
    location = update.message.location
    lat, lon = location.latitude, location.longitude
    
    await update.message.chat.send_action(action="typing")
    await update.message.reply_text("⏳ Fetching weather data for your farm...")
    
    weather_data = get_weather_forecast(lat, lon)
    
    if weather_data:
        # Try to get village/city name (optional)
        location_name = f"{lat:.2f}, {lon:.2f}"
        try:
            geo_url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
            geo_response = requests.get(geo_url, headers={'User-Agent': 'MeghdootBot/1.0'}, timeout=5)
            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                village = geo_data.get('address', {}).get('village') or \
                         geo_data.get('address', {}).get('town') or \
                         geo_data.get('address', {}).get('city')
                if village:
                    location_name = village
        except:
            pass
        
        message = format_weather_message(weather_data, location_name)
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        await update.message.reply_text(
            "❌ Unable to fetch weather data. Please try again.",
            parse_mode='Markdown'
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = (
        "*📖 Meghdoot Help Guide*\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help\n\n"
        "*How to use:*\n"
        "1. Tap '📍 Share Farm Location' button\n"
        "2. Allow location access\n"
        "3. Get instant weather forecast\n\n"
        "*Features:*\n"
        "• Current temperature\n"
        "• 3-day forecast\n"
        "• Farming recommendations\n"
        "• Hyperlocal weather data\n\n"
        "_Powered by Open-Meteo API_ ☁️"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Add handlers to Telegram app
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(CommandHandler("help", help_command))
telegram_app.add_handler(MessageHandler(filters.LOCATION, handle_location))

# ============ FLASK WEBHOOK ROUTES ============
@app.route('/')
def home():
    """Health check endpoint"""
    return "🌾 Meghdoot Weather Bot is running 24/7! ✅"

@app.route('/health')
def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "bot": "Meghdoot",
        "time": datetime.now().isoformat()
    }, 200

@app.route(f'/{TOKEN}', methods=['POST'])
async def webhook():
    """Handle incoming updates from Telegram"""
    try:
        update = Update.de_json(request.get_json(), telegram_app.bot)
        await telegram_app.process_update(update)
        return "OK", 200
    except Exception as e:
        print(f"Webhook error: {e}")
        return "Error", 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Manually set webhook (run once after deployment)"""
    try:
        railway_url = request.host_url.rstrip('/')
        webhook_url = f"{railway_url}/{TOKEN}"
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            telegram_app.bot.set_webhook(url=webhook_url)
        )
        loop.close()
        
        if result:
            return {
                "success": True,
                "message": "Webhook set successfully",
                "url": webhook_url
            }
        else:
            return {"success": False, "message": "Failed to set webhook"}, 500
    except Exception as e:
        return {"success": False, "error": str(e)}, 500

# ============ INITIALIZATION ============
async def init():
    """Initialize bot and set webhook"""
    await telegram_app.initialize()
    print("✅ Meghdoot bot initialized")
    
    # Get Railway URL from environment
    railway_url = os.environ.get('RAILWAY_STATIC_URL')
    if railway_url:
        webhook_url = f"https://{railway_url}/{TOKEN}"
        await telegram_app.bot.set_webhook(url=webhook_url)
        print(f"✅ Webhook set to: {webhook_url}")
    else:
        print("⚠️ RAILWAY_STATIC_URL not set - webhook not configured")

# ============ MAIN ============
if __name__ == "__main__":
    # Initialize bot
    asyncio.run(init())
    
    # Start Flask server
    print(f"🚀 Starting Flask server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)