import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# ⚠️ IMPORTANT: REPLACE THIS WITH YOUR ACTUAL RAILWAY URL!
RAILWAY_URL = "https://meghdoot.up.railway.app/"  # CHANGE THIS!

# Construct URLs
webhook_url = f"{RAILWAY_URL}/{TOKEN}"
api_url = f"https://api.telegram.org/bot{TOKEN}/setWebhook"

print("=" * 60)
print("🔧 MEGHDOOT WEBHOOK SETUP")
print("=" * 60)
print(f"🤖 Bot Token: {TOKEN[:10]}...{TOKEN[-5:]}")
print(f"🌐 Railway URL: {RAILWAY_URL}")
print(f"📡 Webhook URL: {webhook_url}")
print()

# Set webhook
try:
    response = requests.post(api_url, json={"url": webhook_url}, timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        if result.get("ok"):
            print("✅✅✅ WEBHOOK SET SUCCESSFULLY! ✅✅✅")
            print(f"\n📬 Your bot is live at:")
            print(f"   {webhook_url}")
            print(f"\n📱 Telegram Bot:")
            print(f"   https://t.me/MeghdootWeatherBot")
            print(f"\n🌍 Anyone can use it NOW!")
        else:
            print(f"❌ Telegram API Error: {result.get('description')}")
    else:
        print(f"❌ HTTP Error {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ Error: {e}")

print("=" * 60)

# Check webhook status
print("\n📊 Verifying webhook...")
check_url = f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo"
try:
    response = requests.get(check_url)
    data = response.json()
    if data['ok']:
        url = data['result'].get('url', 'Not set')
        print(f"✅ Current webhook: {url}")
        if url == webhook_url:
            print("✅✅✅ VERIFICATION SUCCESSFUL! ✅✅✅")
        else:
            print("❌ Webhook URL mismatch!")
    else:
        print(f"❌ Failed to verify: {data}")
except Exception as e:
    print(f"❌ Verification error: {e}")
print("=" * 60)