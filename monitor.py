import json
import os
import time
import requests
from bs4 import BeautifulSoup

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

state = {}

def send_telegram(message):
    requests.post(
        TELEGRAM_URL,
        json={
            "chat_id": CHAT_ID,
            "text": message
        },
        timeout=30
    )

def is_in_stock(url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=30)

    text = response.text.lower()

    if "sold out" in text:
        return False

    return True

with open("products.json") as f:
    products = json.load(f)["products"]

send_telegram("✅ Amul Stock Monitor Started")

while True:

    for product in products:

        try:
            available = is_in_stock(product["url"])

            previous = state.get(product["name"])

            if previous is None:
                state[product["name"]] = available

            elif previous is False and available is True:

                send_telegram(
                    f"""🚨 AMUL STOCK ALERT

{product['name']} is now IN STOCK

{product['url']}
"""
                )

                state[product["name"]] = True

            elif previous is True and available is False:
                state[product["name"]] = False

        except Exception as e:
            print(e)

    time.sleep(120)
