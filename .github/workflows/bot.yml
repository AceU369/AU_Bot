#!/usr/bin/env python3
"""
Gold.de Verfügbarkeits-Bot v2.0 - FUNKTIONSFÄHIG
"""

import requests
import re
import os
import sys
from datetime import datetime
from time import sleep
from collections import defaultdict

print("=" * 60)
print("🚀 Gold.de Verfügbarkeits-Bot v2.0 startet...")
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
print("=" * 60)

# Telegram Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram Secrets fehlen!")
    sys.exit(1)

# Produkte
PRODUKTE = {
    "Krügerrand 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/kruegerrand/",
    "Maple Leaf 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/canada-maple-leaf/",
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "100g Silberbarren": "https://www.gold.de/kaufen/silberbarren/100-gramm/",
    "250g Silberbarren": "https://www.gold.de/kaufen/silberbarren/250-gramm/",
}

# Händler
HAENDLER = {
    'stonexbullion.com': 'StoneX Bullion',
    'goldsilbershop.de': 'GoldSilberShop',
    'proaurum.de': 'Pro Aurum',
}

HEADERS = {'User-Agent': 'Mozilla/5.0 (GitHub-Actions-Bot)'}

def scrape_produkt(name, url):
    print(f"🔍 {name}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            return None, {}
        
        text = r.text.lower()
        details = defaultdict(int)
        
        for pattern, h_name in HAENDLER.items():
            escaped = pattern.replace('.', r'\.')
            matches = re.findall(escaped, text)
            if matches:
                details[h_name] = len(matches)
        
        total = sum(details.values())
        if total > 0:
            print(f"   ✅ {total} Händler: {dict(details)}")
        else:
            print(f"   ⏸️  Keine Händler")
        
        return total, dict(details)
    except:
        return None, {}

def sende_telegram(text):
    print(f"\n📤 Sende Nachricht...")
    print(f"Länge: {len(text)} Zeichen")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML'
    }
    
    try:
        r = requests.post(url, json=data, timeout=10)
        if r.status_code == 200 and r.json().get('ok'):
            print("✅ Gesendet!")
            return True
    except:
        pass
    return False

def main():
    print(f"\nScanne {len(PRODUKTE)} Produkte...")
    print("-" * 50)
    
    results = []
    for name, url in PRODUKTE.items():
        count, details = scrape_produkt(name, url)
        results.append({'name': name, 'count': count, 'details': details})
        sleep(0.5)
    
    # Nachricht
    msg = f"<b>🏦 Gold.de Report v2.0</b>\n"
    msg += f"⏰ {datetime.now().strftime('%H:%M')}\n\n"
    
    for r in results:
        if r['count']:
            msg += f"• {r['name']}: {r['count']} Händler\n"
            if r['details']:
                for h, c in r['details'].items():
                    msg += f"  - {h}: {c}\n"
    
    msg += f"\n🔄 Nächster Check in 1 Stunde"
    
    sende_telegram(msg)
    print(f"\n✅ Fertig um {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
