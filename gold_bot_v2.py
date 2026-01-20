#!/usr/bin/env python3
"""
Gold.de Verfügbarkeits-Bot v2.0
Stündliche Reports mit detaillierten Händlerlisten
"""

import requests
import re
import os
import sys
from datetime import datetime
from time import sleep
from collections import defaultdict

# === KONFIGURATION ===
print("=" * 60)
print("🚀 Gold.de Verfügbarkeits-Bot v2.0 (NEUE DATEI)")
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
print("=" * 60)

# Telegram Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram Secrets fehlen!")
    sys.exit(1)

print(f"🔐 Telegram Token: {'VORHANDEN' if TELEGRAM_TOKEN else 'FEHLT'}")
print(f"🔐 Telegram Chat-ID: {'VORHANDEN' if TELEGRAM_CHAT_ID else 'FEHLT'}")

# === PRODUKTE mit garantiert funktionierenden URLs ===
PRODUKTE = {
    "Krügerrand 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/kruegerrand/",
    "Maple Leaf 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/canada-maple-leaf/",
    "Wiener Philharmoniker 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/philharmoniker/",
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "5g Goldbarren": "https://www.gold.de/kaufen/goldbarren/5-gramm/",
    "1oz Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-unzen/",
    "100g Goldbarren": "https://www.gold.de/kaufen/goldbarren/100-gramm/",
    "Maple Leaf 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/canada-maple-leaf/",
    "Wiener Philharmoniker 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/silber-philharmoniker/",
    "Krügerrand 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/kruegerrand-silber/",
    "1oz Silberbarren": "https://www.gold.de/kaufen/silberbarren/1-unzen/",
    "100g Silberbarren": "https://www.gold.de/kaufen/silberbarren/100-gramm/",
    "250g Silberbarren": "https://www.gold.de/kaufen/silberbarren/250-gramm/",
    "500g Silberbarren": "https://www.gold.de/kaufen/silberbarren/500-gramm/"
}

# === HÄNDLER-MAPPING ===
HAENDLER_PATTERNS = {
    'stonexbullion.com': 'StoneX Bullion',
    'goldsilbershop.de': 'GoldSilberShop',
    'proaurum.de': 'Pro Aurum',
    'degussa.de': 'Degussa',
    'heubach.de': 'Heubach',
    'esesg.de': 'ES ESG',
    'philoro.de': 'Philoro',
    'classic.gold.de': 'Gold.de Classic',
    'classic.silber.de': 'Silber.de Classic'
}

# User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 GoldBot/2.0'
}

def scrape_produkt(produkt_name, url):
    """Scrapet ein Produkt und gibt detaillierte Händlerinfo zurück."""
    print(f"   🔍 {produkt_name}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=25)
        
        if response.status_code != 200:
            print(f"      ⚠️  Status {response.status_code}")
            return None, {}
            
        html_text = response.text.lower()
        
        # Zähle Händler mit Details - KEINE BACKSLASH PROBLEME!
        haendler_details = defaultdict(int)
        
        for pattern, haendler_name in HAENDLER_PATTERNS.items():
            # Einfache String-Suche statt Regex
            anzahl = html_text.count(pattern)
            if anzahl > 0:
                haendler_details[haendler_name] = anzahl
        
        gesamt_count = sum(haendler_details.values())
        
        if gesamt_count > 0:
            haendler_liste = [f"{h}: {c}" for h, c in sorted(haendler_details.items(), key=lambda x: x[1], reverse=True)]
            print(f"      ✅ {gesamt_count} Händler: {', '.join(haendler_liste[:3])}")
        else:
            print(f"      ⏸️  Keine Händler gefunden")
        
        return gesamt_count, dict(haendler_details)
        
    except Exception as e:
        print(f"      ❌ Fehler: {str(e)[:50]}")
        return None, {}

def sende_telegram(text):
    """Sendet Telegram-Nachricht."""
    print(f"\n📤 Sende Telegram-Nachricht...")
    print(f"📝 Länge: {len(text)} Zeichen")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=data, timeout=15)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('ok'):
            print(f"✅ Telegram-Nachricht gesendet! (ID: {response_data.get('result', {}).get('message_id')})")
            return True
        else:
            print(f"❌ Telegram-Fehler: {response_data}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")
        return False

def erstelle_detailed_report(ergebnisse):
    """Erstellt einen detaillierten Report."""
    if not ergebnisse:
        return "<b>❌ Keine Ergebnisse</b>"
    
    # Sortiere nach Anzahl Händler
    erfolgreiche = [e for e in ergebnisse if e['count'] is not None]
    erfolgreiche.sort(key=lambda x: x['count'], reverse=True)
    
    if not erfolgreiche:
        return "<b>⚠️ Alle Scans fehlgeschlagen</b>"
    
    # Zähle alle Händler
    alle_haendler = defaultdict(int)
    for e in erfolgreiche:
        for h, c in e['details'].items():
            alle_haendler[h] += c
    
    # Baue Nachricht
    nachricht = f"<b>🏦 Gold.de Verfügbarkeits-Report v2.0</b>\n"
    nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    nachricht += f"📊 {len(erfolgreiche)}/{len(PRODUKTE)} Produkte gescannt\n"
    nachricht += f"🏪 {len(alle_haendler)} verschiedene Händler\n\n"
    
    # TOP 3 Produkte
    nachricht += "<b>🏆 TOP 3 PRODUKTE:</b>\n"
    for i, e in enumerate(erfolgreiche[:3], 1):
        sterne = "★" * min(e['count'], 5)
        nachricht += f"{i}. <b>{e['name']}</b>: {e['count']} Händler {sterne}\n"
        
        if e['details']:
            details_str = ", ".join([f"{h}({c})" for h, c in list(e['details'].items())[:3]])
            nachricht += f"   <i>{details_str}</i>\n"
        
        nachricht += "\n"
    
    # Top Händler
    if alle_haendler:
        nachricht += "<b>👑 TOP HÄNDLER INSGESAMT:</b>\n"
        top_haendler = sorted(alle_haendler.items(), key=lambda x: x[1], reverse=True)[:5]
        for h, c in top_haendler:
            nachricht += f"• {h}: <b>{c}</b> Vorkommen\n"
        nachricht += "\n"
    
    # Zusammenfassung
    gesamt = sum(e['count'] for e in erfolgreiche)
    nachricht += f"<b>📈 ZUSAMMENFASSUNG:</b>\n"
    nachricht += f"• Höchste: {erfolgreiche[0]['name']} ({erfolgreiche[0]['count']} Händler)\n"
    
    niedrigste = next((e for e in reversed(erfolgreiche) if e['count'] > 0), None)
    if niedrigste:
        nachricht += f"• Niedrigste: {niedrigste['name']} ({niedrigste['count']} Händler)\n"
    
    nachricht += f"• Gesamt Händlervorkommen: <b>{gesamt}</b>\n"
    
    nachricht += f"\n🔄 Nächster Report in 1 Stunde\n"
    nachricht += f"#GoldBot #{datetime.now().strftime('%Y%m%d_%H')}"
    
    return nachricht

def main():
    """Hauptfunktion."""
    print(f"\n🔍 Starte Scan für {len(PRODUKTE)} Produkte...")
    print("-" * 50)
    
    ergebnisse = []
    
    for produkt_name, url in PRODUKTE.items():
        count, details = scrape_produkt(produkt_name, url)
        ergebnisse.append({
            'name': produkt_name,
            'count': count,
            'details': details
        })
        sleep(0.3)  # Kurze Pause
    
    print("-" * 50)
    
    # Statistik
    erfolgreich = len([e for e in ergebnisse if e['count'] is not None])
    print(f"📊 {erfolgreich}/{len(PRODUKTE)} Produkte erfolgreich")
    
    # Report erstellen und senden
    nachricht = erstelle_detailed_report(ergebnisse)
    
    if sende_telegram(nachricht):
        print("\n🎉 Bot erfolgreich ausgeführt!")
    else:
        print("\n⚠️  Bot ausgeführt, aber Telegram-Sendung fehlgeschlagen")
    
    print(f"\n✅ Bot beendet um {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
