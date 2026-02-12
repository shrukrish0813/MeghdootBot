import os
import requests
from dotenv import load_dotenv
import sys

print("=" * 60)
print("🔍 MEGHDOOT DEPLOYMENT DIAGNOSTIC")
print("=" * 60)

# Load environment
load_dotenv()
token = os.getenv('TELEGRAM_TOKEN')

# 1. CHECK TOKEN
print("\n1. CHECKING BOT TOKEN")
print("-" * 40)
if token:
    print(f"✅ Token found: {token[:10]}...{token[-5:]}")
    print(f"   Length: {len(token)} characters")
else:
    print("❌ Token NOT found in .env file!")
    sys.exit(1)

# 2. CHECK TELEGRAM API
print("\n2. CHECKING TELEGRAM API CONNECTION")
print("-" * 40)
try:
    response = requests.get(f'https://api.telegram.org/bot{token}/getMe', timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            bot = data['result']
            print(f"✅ Bot connected: @{bot['username']}")
            print(f"   Bot ID: {bot['id']}")
            print(f"   Bot name: {bot['first_name']}")
        else:
            print(f"❌ API Error: {data.get('description')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
except Exception as e:
    print(f"❌ Connection Error: {e}")

# 3. CHECK WEBHOOK STATUS
print("\n3. CHECKING WEBHOOK STATUS")
print("-" * 40)
try:
    response = requests.get(f'https://api.telegram.org/bot{token}/getWebhookInfo', timeout=10)
    if response.status_code == 200:
        data = response.json()
        if data['ok']:
            url = data['result'].get('url', 'Not set')
            pending = data['result'].get('pending_update_count', 0)
            print(f"📡 Webhook URL: {url}")
            print(f"⏳ Pending updates: {pending}")
            
            if url and url != '':
                print("✅ Webhook is SET")
                if 'railway' in url.lower():
                    print("   ✅ Railway webhook detected")
                else:
                    print("   ⚠️ Not a Railway URL")
            else:
                print("❌ Webhook is NOT set")
        else:
            print(f"❌ API Error: {data.get('description')}")
    else:
        print(f"❌ HTTP Error: {response.status_code}")
except Exception as e:
    print(f"❌ Connection Error: {e}")

# 4. TEST RAILWAY URL
print("\n4. TESTING RAILWAY DEPLOYMENT")
print("-" * 40)
if url and url != '':
    base_url = url.split('/' + token)[0]
    try:
        response = requests.get(base_url, timeout=10)
        print(f"🌐 Railway URL: {base_url}")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Response: {response.text[:100]}")
            print("   ✅ Railway is responding!")
        else:
            print(f"   ❌ Railway returned status {response.status_code}")
    except Exception as e:
        print(f"   ❌ Cannot reach Railway: {e}")
else:
    print("   ⚠️ No webhook URL to test")

# 5. CHECK ENVIRONMENT VARIABLES ON RAILWAY
print("\n5. RAILWAY ENVIRONMENT CHECK")
print("-" * 40)
print("   To check Railway environment variables:")
print("   1. Go to https://railway.app/dashboard")
print("   2. Click your project")
print("   3. Click 'Variables' tab")
print("   4. Verify these variables exist:")
print("      - TELEGRAM_TOKEN")
print("      - PORT (should be 5000)")

print("\n" + "=" * 60)
print("✅ DIAGNOSTIC COMPLETE")
print("=" * 60)