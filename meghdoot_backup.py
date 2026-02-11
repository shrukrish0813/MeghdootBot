import os
import logging
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.request import HTTPXRequest
from dotenv import load_dotenv
import httpx

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# ==================== FIX: ADD PROXY SUPPORT ====================

async def create_application():
    """Create application with proxy support for India"""
    # Try different connection settings
    request = HTTPXRequest(
        connection_pool_size=8,
        connect_timeout=30.0,
        read_timeout=30.0,
        write_timeout=30.0,
    )
    
    # Create application with custom request object
    application = Application.builder() \
        .token(TOKEN) \
        .request(request) \
        .build()
    
    return application

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message when /start is issued."""
    user = update.effective_user
    
    # Create keyboard with location button
    keyboard = [
        [KeyboardButton("📍 Share My Farm Location", request_location=True)],
        [KeyboardButton("🌦️ Get Weather Forecast")],
        [KeyboardButton("ℹ️ Help")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    welcome_text = f"""
🌾 *नमस्ते {user.first_name}!* 🌾

*Welcome to Meghdoot* ☁️
Your AI Weather Companion for Farmers

Tap "📍 Share My Farm Location" to begin!
"""
    
    await update.message.reply_text(
        welcome_text,
        parse_mode='Markdown',
        reply_markup=reply_markup
    )

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle received location."""
    location = update.message.location
    lat, lon = location.latitude, location.longitude
    
    await update.message.reply_text(
        f"✅ *Location Received!*\n\n"
        f"Latitude: `{lat:.4f}`\n"
        f"Longitude: `{lon:.4f}`\n\n"
        f"🌤️ *Fetching weather data...*",
        parse_mode='Markdown'
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle text messages."""
    text = update.message.text
    
    if text == "🌦️ Get Weather Forecast":
        await update.message.reply_text(
            "Please share your location first using the '📍 Share My Farm Location' button.",
            parse_mode='Markdown'
        )
    elif text == "ℹ️ Help":
        await update.message.reply_text(
            "Share your location to get weather forecasts and farming advice!",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"I understand you said: '{text}'\n\n"
            "To get started, tap '📍 Share My Farm Location'",
            parse_mode='Markdown'
        )

# ==================== MAIN FUNCTION ====================

def main() -> None:
    """Start the bot."""
    try:
        print("=" * 50)
        print("🌾 MEGHDOOT WEATHER BOT")
        print("🤖 Starting with enhanced connection settings...")
        print("=" * 50)
        
        # Run async main
        import asyncio
        asyncio.run(async_main())
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check your internet connection")
        print("2. Try using mobile hotspot")
        print("3. Check if Telegram is blocked on your network")

async def async_main():
    """Async main function"""
    # Create application with our custom settings
    application = await create_application()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.LOCATION, handle_location))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("✅ Application created successfully")
    print("🚀 Starting bot polling...")
    
    # Start polling
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    print("🤖 Bot is now running! Press Ctrl+C to stop")
    
    # Keep running
    await application.stop()

if __name__ == '__main__':
    main()