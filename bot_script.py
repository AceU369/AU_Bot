#!/usr/bin/env python3
"""
Gold.de Verfügbarkeits-Bot v2.0
Mit stündlichen Reports und detaillierten Händlerlisten
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
    "Krügerrand 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/kruegerrand/",
    "Maple Leaf 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/canada-maple-leaf/",
    "Wiener Philharmoniker 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/philharmoniker/",
    "Britannia 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/britannia/",
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

# === HÄNDLER-MAPPING für bessere Lesbarkeit ===
HAENDLER_PATTERNS = {
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

def scrape_produkt(produkt_name, url):
    """Scrapet ein Produkt und gibt detaillierte Händlerinfo zurück."""
    print(f"   🔍 {produkt_name}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=25)
        
        if response.status_code != 200:
            print(f"      ⚠️  Status {response.status_code}")
            return None, {}
            
        html_text = response.text.lower()
        
        # Zähle Händler mit Details
        haendler_details = defaultdict(int)
        for pattern, haendler_name in HAENDLER_PATTERNS.items():
            # Escape dots für regex
            escaped_pattern = pattern.replace('.', r'\.')
            matches = re.findall(escaped_pattern, html_text)
            if matches:
                haendler_details[haendler_name] = len(matches)
        
        gesamt_count = sum(haendler_details.values())
        
        # DEBUG: Was wurde gefunden?
        print(f"      🔎 DEBUG: Gefundene Händler: {dict(haendler_details)}")
        print(f"      🔎 DEBUG: HTML Länge: {len(html_text)} Zeichen")
        
        # Formatierte Händlerliste für Ausgabe
        haendler_liste = []
        for haendler, anzahl in sorted(haendler_details.items(), key=lambda x: x[1], reverse=True):
            haendler_liste.append(f"{haendler}: {anzahl}")
        
        if gesamt_count > 0:
            print(f"      ✅ {gesamt_count} Händler: {', '.join(haendler_liste[:3])}")
        else:
            print(f"      ⏸️  Keine Händler gefunden")
        
        return gesamt_count, dict(haendler_details)
        
    except Exception as e:
        print(f"      ❌ Fehler: {str(e)[:80]}")
        return None, {}

def sende_telegram(text):
    """Sendet Telegram-Nachricht mit Debug-Ausgabe."""
    print(f"\n📤 Sende Telegram-Nachricht...")
    print(f"📝 Nachricht (erste 300 Zeichen):")
    print("-" * 60)
    print(text[:300])
    print("-" * 60)
    print(f"📝 Gesamtlänge: {len(text)} Zeichen")
    
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
        
        if response.status_code == 200:
            response_json = response.json()
            print(f"📄 Response: {response_json}")
            
            if response_json.get('ok'):
                print("✅ Telegram-Nachricht erfolgreich gesendet!")
                print(f"📨 Nachricht-ID: {response_json.get('result', {}).get('message_id', 'unbekannt')}")
                return True
            else:
                print(f"❌ Telegram-API-Fehler: {response_json.get('description')}")
                return False
        else:
            print(f"❌ HTTP-Fehler: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception beim Senden: {e}")
        return False

def erstelle_detailed_report(ergebnisse):
    """Erstellt einen detaillierten Report mit Händlerlisten."""
    if not ergebnisse:
        return "❌ Keine Ergebnisse zum Berichten"
    
    # Sortiere nach Anzahl Händler (absteigend)
    ergebnisse.sort(key=lambda x: x['count'] if x['count'] is not None else -1, reverse=True)
    
    # Zähle alle Händler insgesamt
    alle_haendler = defaultdict(int)
    for e in ergebnisse:
        if e['haendler_details']:
            for haendler, count in e['haendler_details'].items():
                alle_haendler[haendler] += count
    
    # Baue Nachricht
    nachricht = f"<b>🏦 Gold.de Verfügbarkeits-Report v2.0</b>\n"
    nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    nachricht += f"📊 {len([e for e in ergebnisse if e['count'] is not None])}/{len(PRODUKTE)} Produkte\n"
    nachricht += f"🏪 {len(alle_haendler)} verschiedene Händler\n\n"
    
    # TOP 3 Produkte mit Details
    nachricht += "<b>🏆 TOP 3 PRODUKTE:</b>\n"
    top_count = 0
    for i, e in enumerate(ergebnisse[:3], 1):
        if e['count'] is not None and e['count'] > 0:
            sterne = "★" * min(e['count'], 5)
            nachricht += f"{i}. <b>{e['name']}</b>: {e['count']} Händler {sterne}\n"
            
            # Händlerliste (max 3)
            if e['haendler_details']:
                haendler_str = ", ".join([f"{h}({c})" for h, c in list(e['haendler_details'].items())[:3]])
                nachricht += f"   <i>{haendler_str}</i>\n"
            else:
                nachricht += f"   <i>Keine spezifischen Händler</i>\n"
            
            nachricht += "\n"
            top_count += 1
    
    if top_count == 0:
        nachricht += "<i>Keine Produkte mit Händlern gefunden</i>\n\n"
    
    # Top Händler insgesamt
    if alle_haendler:
        nachricht += "<b>👑 TOP HÄNDLER INSGESAMT:</b>\n"
        top_haendler = sorted(alle_haendler.items(), key=lambda x: x[1], reverse=True)[:5]
        for haendler, count in top_haendler:
            nachricht += f"• {haendler}: <b>{count}</b> Vorkommen\n"
        nachricht += "\n"
    
    # Zusammenfassung
    erfolgreiche_scans = [e for e in ergebnisse if e['count'] is not None]
    if erfolgreiche_scans:
        nachricht += "<b>📈 ZUSAMMENFASSUNG:</b>\n"
        nachricht += f"• Höchste Verfügbarkeit: {ergebnisse[0]['name']} ({ergebnisse[0]['count'] or 0} Händler)\n"
        
        # Finde niedrigste Verfügbarkeit (aber > 0)
        niedrigste = next((e for e in reversed(ergebnisse) if e['count'] is not None and e['count'] > 0), None)
        if niedrigste:
            nachricht += f"• Niedrigste Verfügbarkeit: {niedrigste['name']} ({niedrigste['count']} Händler)\n"
        
        gesamt_anzahl = sum(e['count'] or 0 for e in ergebnisse)
        nachricht += f"• Gesamt Händlervorkommen: <b>{gesamt_anzahl}</b>\n"
    
    nachricht += f"\n🔄 Nächster Check in 1 Stunde\n"
    nachricht += f"#GoldBot #{datetime.now().strftime('%Y%m%d_%H')}"
    
    return nachricht

def main():
    """Hauptfunktion - stündlicher Report."""
    print(f"\n🔍 Starte Verfügbarkeits-Check für {len(PRODUKTE)} Produkte...")
    print("-" * 50)
    
    ergebnisse = []
    
    for produkt_name, url in PRODUKTE.items():
        count, haendler_details = scrape_produkt(produkt_name, url)
        
        ergebnisse.append({
            'name': produkt_name,
            'count': count,
            'haendler_details': haendler_details
        })
        
        # Kurze Pause zwischen Requests
        sleep(0.5)
    
    print("-" * 50)
    
    # Zähle erfolgreiche Scans
    erfolgreich = len([e for e in ergebnisse if e['count'] is not None])
    print(f"📊 {erfolgreich}/{len(PRODUKTE)} Produkte erfolgreich gescannt")
    
    # Erstelle und sende Report
    nachricht = erstelle_detailed_report(ergebnisse)
    
    if sende_telegram(nachricht):
        print("\n🎉 Bot erfolgreich ausgeführt!")
    else:
        print("\n⚠️  Bot ausgeführt, aber Telegram-Sendung fehlgeschlagen")
    
    print(f"\n✅ Bot beendet um {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
