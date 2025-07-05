import requests
import os
from datetime import datetime
from openai import OpenAI
import schedule
import time
import telegram

# API-KEYS
FOOTBALL_API_KEY = os.getenv("FOOTBALL_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# GPT Client
client = OpenAI(api_key=OPENAI_API_KEY)

# Daten abrufen
def get_matches():
    url = "https://v3.football.api-sports.io/fixtures?date=" + datetime.now().strftime('%Y-%m-%d')
    headers = {
        "x-apisports-key": FOOTBALL_API_KEY
    }
    response = requests.get(url, headers=headers)
    return response.json()

# Analyse generieren
def generate_analysis(home, away):
    prompt = f"Predict the outcome and betting tip for the football match between {home} and {away}. Provide analysis in 1-2 sentences."
    try:
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"❌ Analysefehler: {str(e)}"

# Telegram senden
def send_to_telegram(message):
    bot = telegram.Bot(token=TELEGRAM_BOT_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode="HTML")

# Hauptfunktion
def daily_task():
    matches = get_matches()
    text = f"📅 {datetime.now().strftime('%d.%m.%Y')} – Zenginsin Tipps\n\n⚽️ Fußball:\n"
    
    for game in matches.get("response", [])[:3]:  # Max 3 Spiele
        teams = game["teams"]
        home = teams["home"]["name"]
        away = teams["away"]["name"]
        time_str = game["fixture"]["date"][11:16]
        league = game["league"]["name"]

        analysis = generate_analysis(home, away)
        text += f"🕒 {time_str} – {home} vs {away} ({league})\n📊 GPT-Tipp: {analysis}\n\n"

    send_to_telegram(text)

# Planen
schedule.every().day.at("10:35").do(daily_task)

if __name__ == "__main__":
    daily_task()  # Für sofortigen Test
    while True:
        schedule.run_pending()
        time.sleep(60)
