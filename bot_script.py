#!/usr/bin/env python3
"""
Gold.de Verfügbarkeits-Bot v2.0
Mit stündlichen Reports, spezifischen Befehlen und detaillierten Händlerlisten
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
print("🚀 Gold.de Verfügbarkeits-Bot v2.0 startet...")
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
print("=" * 60)

# Telegram Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram Secrets fehlen!")
    sys.exit(1)

print(f"🔐 Telegram Token vorhanden: {'JA' if TELEGRAM_TOKEN else 'NEIN'}")
print(f"🔐 Telegram Chat-ID vorhanden: {'JA' if TELEGRAM_CHAT_ID else 'NEIN'}")

# === PRODUKTE mit GETESTETEN URLs ===
PRODUKTE = {
    "krugerrand_gold": {
        "name": "Krügerrand 1oz Gold",
        "url": "https://www.gold.de/kaufen/goldmuenzen/kruegerrand/",
        "command": "/krugerrandgold"
    },
    "mapleleaf_gold": {
        "name": "Maple Leaf 1oz Gold", 
        "url": "https://www.gold.de/kaufen/goldmuenzen/canada-maple-leaf/",
        "command": "/mapleleafgold"
    },
    "philharmoniker_gold": {
        "name": "Wiener Philharmoniker 1oz Gold",
        "url": "https://www.gold.de/kaufen/goldmuenzen/philharmoniker/",
        "command": "/philharmonikergold"
    },
    "britannia_gold": {
        "name": "Britannia 1oz Gold",
        "url": "https://www.gold.de/kaufen/goldmuenzen/britannia/",
        "command": "/britanniagold"
    },
    "1g_goldbarren": {
        "name": "1g Goldbarren",
        "url": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
        "command": "/1ggold"
    },
    "5g_goldbarren": {
        "name": "5g Goldbarren",
        "url": "https://www.gold.de/kaufen/goldbarren/5-gramm/",
        "command": "/5ggold"
    },
    "1oz_goldbarren": {
        "name": "1oz Goldbarren",
        "url": "https://www.gold.de/kaufen/goldbarren/1-unzen/",
        "command": "/1ozgold"
    },
    "100g_goldbarren": {
        "name": "100g Goldbarren", 
        "url": "https://www.gold.de/kaufen/goldbarren/100-gramm/",
        "command": "/100ggold"
    },
    "mapleleaf_silber": {
        "name": "Maple Leaf 1oz Silber",
        "url": "https://www.gold.de/kaufen/silbermuenzen/canada-maple-leaf/",
        "command": "/mapleleafsilber"
    },
    "philharmoniker_silber": {
        "name": "Wiener Philharmoniker 1oz Silber",
        "url": "https://www.gold.de/kaufen/silbermuenzen/silber-philharmoniker/",
        "command": "/philharmonikersilber"
    },
    "krugerrand_silber": {
        "name": "Krügerrand 1oz Silber",
        "url": "https://www.gold.de/kaufen/silbermuenzen/kruegerrand-silber/",
        "command": "/krugerrandsilber"
    },
    "1oz_silberbarren": {
        "name": "1oz Silberbarren",
        "url": "https://www.gold.de/kaufen/silberbarren/1-unzen/",
        "command": "/1ozsilber"
    },
    "100g_silberbarren": {
        "name": "100g Silberbarren",
        "url": "https://www.gold.de/kaufen/silberbarren/100-gramm/",
        "command": "/100gsilber"
    },
    "250g_silberbarren": {
        "name": "250g Silberbarren",
        "url": "https://www.gold.de/kaufen/silberbarren/250-gramm/",
        "command": "/250gsilber"
    },
    "500g_silberbarren": {
        "name": "500g Silberbarren",
        "url": "https://www.gold.de/kaufen/silberbarren/500-gramm/",
        "command": "/500gsilber"
    }
}

# === HÄNDLER-MAPPING für bessere Lesbarkeit ===
HAENDLER_NAMEN = {
    'stonexbullion.com': 'StoneX Bullion',
    'goldsilbershop.de': 'GoldSilberShop',
    'proaurum.de': 'Pro Aurum',
    'degussa.de': 'Degussa',
    'heubach.de': 'Heubach',
    'esesg.de': 'ES ESG',
    'philoro.de': 'Philoro',
    'classic.gold.de': 'Gold.de Classic',
    'classic.silber.de': 'Silber.de Classic',
    'bullionvault.com': 'BullionVault',
    'aurinum.de': 'Aurinum',
    'cash.gold.de': 'Gold.de Cash'
}

# User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (GitHub-Actions-Bot/2.0; +https://github.com/AceU369/AU_Bot)'
}

def scrape_produkt(produkt_key, produkt_info):
    """Scrapet ein Produkt und gibt detaillierte Händlerinfo zurück."""
    name = produkt_info["name"]
    url = produkt_info["url"]
    
    print(f"   🔍 {name}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=25)
        
        if response.status_code != 200:
            print(f"      ⚠️  Status {response.status_code}")
            return None, None, None
            
        html_text = response.text.lower()
        
        # Zähle Händler mit Details
        haendler_details = defaultdict(int)
        for pattern, haendler_name in HAENDLER_NAMEN.items():
            pattern_lower = pattern.lower()
            matches = len(re.findall(rf'{pattern_lower.replace(".", "\.")}', html_text))
            if matches > 0:
                haendler_details[haendler_name] = matches
        
        gesamt_count = sum(haendler_details.values())
        
        # Formatierte Händlerliste
        haendler_liste = []
        for haendler, anzahl in sorted(haendler_details.items(), key=lambda x: x[1], reverse=True):
            haendler_liste.append(f"{haendler}: {anzahl}")
        
        if gesamt_count > 0:
            print(f"      ✅ {gesamt_count} Händler: {', '.join(haendler_liste[:3])}")
        else:
            print(f"      ⏸️  Keine Händler gefunden")

                # DEBUG: Was wurde gefunden?
        print(f"      🔎 DEBUG: Gefundene Händler: {dict(haendler_details)}")
        print(f"      🔎 DEBUG: HTML Länge: {len(html_text)} Zeichen")
        
        # Suche nach einem bekannten Händler im HTML
        if "goldsilbershop.de" in html_text:
            print(f"      ✅ goldsilbershop.de im HTML gefunden!")
        else:
            print(f"      ❌ goldsilbershop.de NICHT im HTML gefunden!")
        
        return gesamt_count, haendler_details, haendler_liste
        
        return gesamt_count, haendler_details, haendler_liste
        
    except Exception as e:
        print(f"      ❌ Fehler: {str(e)[:50]}")
        return None, None, None

def sende_telegram(text):
    """Sendet Telegram-Nachricht."""
    print(f"\n📤 TEST: Sende Telegram-Nachricht...")
    print(f"📝 Nachricht (erste 200 Zeichen):")
    print("-" * 50)
    print(text[:200])
    print("-" * 50)
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"📡 Telegram API Response: {response.status_code}")
        print(f"📄 Response JSON: {response.json()}")
        
        if response.status_code == 200 and response.json().get('ok'):
            print("✅ Telegram-Nachricht erfolgreich gesendet!")
            return True
        else:
            print("❌ Telegram-API-Fehler!")
            return False
    except Exception as e:
        print(f"❌ Exception beim Senden: {e}")
        return False

def erstelle_komplett_report(ergebnisse):
    """Erstellt einen kompletten stündlichen Report."""
    if not ergebnisse:
        return None
    
    # Sortieren
    ergebnisse.sort(key=lambda x: x['count'], reverse=True)
    
    # Gesamthändler zählen
    alle_haendler = defaultdict(int)
    for e in ergebnisse:
        for haendler, count in e['haendler_details'].items():
            alle_haendler[haendler] += count
    
    # Top 10 Händler insgesamt
    top_haendler = sorted(alle_haendler.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Nachricht bauen
    nachricht = f"<b>🏦 Gold.de Stündlicher Report</b>\n"
    nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    nachricht += f"📊 {len(ergebnisse)}/{len(PRODUKTE)} Produkte\n"
    nachricht += f"🏪 {len(alle_haendler)} verschiedene Händler\n\n"
    
    nachricht += "<b>🏆 TOP 3 PRODUKTE:</b>\n"
    for i, e in enumerate(ergebnisse[:3], 1):
        sterne = "★" * min(e['count'], 5)
        haendler_str = ", ".join([f"{h}:{c}" for h, c in list(e['haendler_details'].items())[:3]])
        nachricht += f"{i}. {e['name']}: <b>{e['count']}</b> {sterne}\n"
        nachricht += f"   <i>{haendler_str}</i>\n"
    
    nachricht += f"\n<b>👑 TOP HÄNDLER INSGESAMT:</b>\n"
    for haendler, count in top_haendler[:5]:
        nachricht += f"• {haendler}: <b>{count}</b> Vorkommen\n"
    
    nachricht += f"\n<b>📈 ZUSAMMENFASSUNG:</b>\n"
    nachricht += f"• Höchste: {ergebnisse[0]['name']} ({ergebnisse[0]['count']} Händler)\n"
    nachricht += f"• Niedrigste: {ergebnisse[-1]['name']} ({ergebnisse[-1]['count']} Händler)\n"
    nachricht += f"• Gesamt: <b>{sum(e['count'] for e in ergebnisse)}</b> Händlervorkommen\n"
    
    nachricht += f"\n<b>🔄 Nächster Report in 1 Stunde</b>\n"
    nachricht += f"<i>Verwende /help für Einzelabfragen</i>\n"
    nachricht += f"#GoldBot #{datetime.now().strftime('%Y%m%d_%H')}"
    
    return nachricht

def erstelle_einzelreport(produkt_key, produkt_info, count, haendler_details, haendler_liste):
    """Erstellt einen Report für ein einzelnes Produkt."""
    if count is None:
        return f"<b>❌ {produkt_info['name']}</b>\nScan fehlgeschlagen."
    
    nachricht = f"<b>🔍 {produkt_info['name']}</b>\n"
    nachricht += f"🌐 {produkt_info['url']}\n"
    nachricht += f"⏰ {datetime.now().strftime('%H:%M')}\n\n"
    
    nachricht += f"<b>Verfügbarkeit:</b> <code>{count} Händler</code>\n\n"
    
    if count > 0:
        nachricht += "<b>Gefundene Händler:</b>\n"
        for haendler_eintrag in haendler_liste:
            nachricht += f"• {haendler_eintrag}\n"
    else:
        nachricht += "⚠️ <i>Derzeit bei keinem Händler verfügbar</i>\n"
    
    nachricht += f"\n<i>ℹ️ Kompletter Report alle 60 Minuten</i>"
    
    return nachricht

def main():
    """Hauptfunktion - stündlicher Report."""
    print(f"\n🔍 Starte stündlichen Check für {len(PRODUKTE)} Produkte...")
    print("-" * 50)
    
    ergebnisse = []
    erfolgreich = 0
    
    for produkt_key, produkt_info in PRODUKTE.items():
        count, haendler_details, haendler_liste = scrape_produkt(produkt_key, produkt_info)
        
        if count is not None:
            ergebnisse.append({
                'key': produkt_key,
                'name': produkt_info['name'],
                'count': count,
                'haendler_details': haendler_details,
                'haendler_liste': haendler_liste,
                'command': produkt_info['command']
            })
            erfolgreich += 1
        else:
            print(f"   ⚠️  {produkt_info['name']}: Scan fehlgeschlagen")
    
    print("-" * 50)
    print(f"✅ {erfolgreich}/{len(PRODUKTE)} Produkte erfolgreich gescannt")
    
    # Kompletter Report
    if ergebnisse:
        nachricht = erstelle_komplett_report(ergebnisse)
        print("\n📤 Sende stündlichen Report...")
        
        if sende_telegram(nachricht):
            print("✅ Stündlicher Report gesendet!")
        else:
            print("❌ Fehler beim Senden des Reports")
    
    print(f"\n🏁 Bot beendet um {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
