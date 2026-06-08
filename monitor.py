import json
import os
import time
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN environment variable missing")

if not CHAT_ID:
    raise Exception("CHAT_ID environment variable missing")

TELEGRAM_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

CHECK_INTERVAL_SECONDS = 120

state = {}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
}


def send_telegram(message):
    try:
        response = requests.post(
            TELEGRAM_URL,
            json={
                "chat_id": CHAT_ID,
                "text": message
            },
            timeout=30
        )

        print(f"Telegram response: {response.status_code}")

    except Exception as e:
        print(f"Telegram send failed: {e}")


def is_in_stock(url):
    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    page_text = response.text.lower()

    print(page_text[:5000])

    return False


def load_products():
    with open("products.json", "r", encoding="utf-8") as f:
        return json.load(f)["products"]


def monitor():
    products = load_products()

    send_telegram("✅ Amul Stock Monitor Started")

    print("Stock monitor started...")

    while True:

        for product in products:

            try:
                name = product["name"]
                url = product["url"]

                available = is_in_stock(url)

                print(
                    f"{name} | "
                    f"{'IN STOCK' if available else 'OUT OF STOCK'}"
                )

                previous = state.get(name)

                if previous is None:
                    state[name] = available

                elif previous is False and available is True:

                    send_telegram(
                        f"""🚨 AMUL STOCK ALERT

{name} is now IN STOCK

{url}
"""
                    )

                    state[name] = True

                elif previous is True and available is False:

                    print(f"{name} went out of stock")

                    state[name] = False

            except Exception as e:
                print(
                    f"Error checking "
                    f"{product.get('name', 'unknown')}: {e}"
                )

        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    monitor()
