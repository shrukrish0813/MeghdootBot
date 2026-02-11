# -*- coding: utf-8 -*-
import os
import requests
import json
from datetime import datetime
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# ============ CONFIGURATION ============
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# ============ WEATHER FUNCTIONS ============
def get_weather_forecast(lat, lon):
    try:
        params = {
            "lat": lat,
            "lon": lon,
            "appid": WEATHER_API_KEY,
            "units": "metric",
            "lang": "en"
        }
        built_url = WEATHER_URL + f"?latitude={lat}&longitude={lon}&hourly=temperature_2m"
        response = requests.get(built_url, timeout=10)
        print(response.json())
        response.raise_for_status()
        return response.json()
    except:
        return None

def format_weather_message(weather_data, location_name="Your Farm"):
    if not weather_data:
        return "❌ Unable to fetch weather data."

    try:
        # Extract data from Open-Meteo API format
        hourly = weather_data.get('hourly', {})
        times = hourly.get('time', [])
        temps = hourly.get('temperature_2m', [])
        
        if not times or not temps:
            return "❌ Incomplete weather data received."
        
        # Get current time index (first hour)
        current_temp = temps[0]
        
        # Calculate daily min/max for next 3 days
        today_forecast = []
        for day in range(3):  # Next 3 days
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
        
        # Build the message
        message = f"🌾 *Meghdoot Weather Advisory* 🌾\n"
        message += f"📍 *Location:* {location_name}\n"
        message += f"⏰ *Time:* {datetime.now().strftime('%d %b %Y, %I:%M %p')}\n\n"
        
        message += f"*🌡️ CURRENT CONDITIONS:*\n"
        message += f"• Temperature: {current_temp:.1f}°C\n"
        message += f"\n"
        
        message += f"*📅 3-DAY FORECAST:*\n"
        for i, day in enumerate(today_forecast[:3]):
            day_name = day['date'].strftime('%a')
            day_date = day['date'].strftime('%d %b')
            message += f"• {day_name}, {day_date}: {day['min']:.0f}-{day['max']:.0f}°C\n"
        
        message += f"\n*⚠️ FARMING RECOMMENDATIONS:*\n"
        
        # Temperature based advice
        if current_temp > 35:
            message += "• 🔥 Heat stress risk - irrigate early morning, provide shade\n"
        elif current_temp > 32:
            message += "• ☀️ High temperature - ensure adequate irrigation\n"
        elif current_temp < 10:
            message += "• ❄️ Frost risk - protect sensitive crops with covers\n"
        elif current_temp < 15:
            message += "• 🌡️ Cool conditions - delay planting of heat-sensitive crops\n"
        else:
            message += "• 🌡️ Normal temperature range - regular farming activities\n"
        
        # Temperature swing advice (from forecast)
        if today_forecast:
            today_swing = today_forecast[0]['max'] - today_forecast[0]['min']
            if today_swing > 15:
                message += "• 📊 Large temperature swing - monitor crop stress\n"
        
        # General farming advice
        message += "• 🌱 Inspect crops regularly for pest and disease\n"
        message += "• 💧 Water plants in early morning or late evening\n"
        message += "• 📋 Plan harvesting activities around weather conditions\n"
        
        message += f"\n_Data: Open-Meteo | Free Weather API_ ☁️\n"
        message += f"🔄 Send location again for updated forecast"
        
        return message
    
    except Exception as e:
        print(f"Error formatting weather: {e}")
        import traceback
        traceback.print_exc()
        return "❌ Error processing weather data. Please try again."
    
    
# ============ TELEGRAM HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("📍 Share Farm Location", request_location=True)]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "🌾 Welcome to Meghdoot Weather Bot!\n\nShare your location to get weather forecast.",
        reply_markup=reply_markup
    )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    location = update.message.location
    lat, lon = location.latitude, location.longitude

    await update.message.chat.send_action(action="typing")
    await update.message.reply_text("⏳ Fetching weather data...")

    weather_data = get_weather_forecast(lat, lon)
   
    if weather_data:
        message = format_weather_message(weather_data, f"{lat:.2f}, {lon:.2f}")
        await update.message.reply_text(message)
    else:
        await update.message.reply_text("❌ Weather API Error. Check your API key. ")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n/start - Start bot\n/help - Show help\n\nShare location for weather forecast."
    )

# ============ MAIN ============
def main():
    print("=" * 50)
    print("🌾 MEGHDOOT WEATHER BOT")
    print("=" * 50)

    if not TELEGRAM_TOKEN:
        print("❌ TELEGRAM_TOKEN not found")
        return
    if not WEATHER_API_KEY:
        print("❌ WEATHER_API_KEY not found")
        return

    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    print("✅ Bot is running!")
    app.run_polling()

if __name__ == "__main__":
    main()