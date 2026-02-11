import os 
from dotenv import load_dotenv 
 
load_dotenv() 
token = os.getenv("TELEGRAM_TOKEN") 
 
if token: 
    print("? Token loaded successfully") 
    print(f"First 10 chars: {token[:10]}...") 
    print(f"Token length: {len(token)} characters") 
else: 
    print("? No token found in .env file") 
