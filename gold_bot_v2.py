#!/usr/bin/env python3
"""
Gold.de Verfügbarkeits-Bot - Optimierte Version
Priorität: Münzen (stündlich), Barren (alle 3 Stunden)
"""

import requests
import os
import sys
from datetime import datetime
from time import sleep
from collections import defaultdict

print("=" * 60)
print("🚀 Gold.de Verfügbarkeits-Bot - OPTIMIERT")
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
print("=" * 60)

# Telegram Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram Secrets fehlen!")
    sys.exit(1)

# === OPTIMIERTE PRODUKTLISTE ===
# Priorität 1: MÜNZEN (stündlich) - 8 Produkte
MUENZEN = {
    # GOLDMÜNZEN 1oz
    "Krügerrand 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/kruegerrand/",
    "Maple Leaf 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/canada-maple-leaf/",
    "Wiener Philharmoniker 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/philharmoniker/",
    "American Eagle 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/american-eagle/",
    
    # GOLDMÜNZEN 1/2oz
    "Gold-Euro 1/2oz": "https://www.gold.de/kaufen/goldmuenzen/euro/",
    
    # SILBERMÜNZEN 1oz
    "Krügerrand 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/kruegerrand-silber/",
    "Maple Leaf 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/canada-maple-leaf/",
    "Wiener Philharmoniker 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/silber-philharmoniker/",
    
    # SILBERMÜNZEN 10oz
    "Arche Noah 10oz Silber": "https://www.gold.de/kaufen/silbermuenzen/arche-noah/",
}

# Priorität 2: BARREN (alle 3 Stunden) - 6 Produkte
BARREN = {
    # GOLDBARREN
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "5g Goldbarren": "https://www.gold.de/kaufen/goldbarren/5-gramm/",
    "1oz Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-unzen/",
    
    # SILBERBARREN  
    "1oz Silberbarren": "https://www.gold.de/kaufen/silberbarren/1-unzen/",
    "50g Silberbarren": "https://www.gold.de/kaufen/silberbarren/50-gramm/",
    "100g Silberbarren": "https://www.gold.de/kaufen/silberbarren/100-gramm/",
}

# Kombinierte Liste für stündlichen Scan
PRODUKTE = {**MUENZEN, **BARREN}

# === ERWEITERTE HÄNDLERLISTE ===
HAENDLER = {
    # Bekannte große Händler
    'goldsilbershop.de': 'GoldSilberShop',
    'stonexbullion.com': 'StoneX Bullion',
    'proaurum.de': 'Pro Aurum',
    'degussa.de': 'Degussa',
    
    # Neue/weitere Händler
    'heubach.de': 'Heubach Edelmetalle',
    'esesg.de': 'ESG Edelmetall-Service',
    'muenzeoesterreich.at': 'Münze Österreich',
    'muenze-oesterreich.at': 'Münze Österreich',
    'anlagegold24.de': 'Anlagegold24',
    'aurargentum.de': 'Aurargentum',
    'mp-edelmetalle.de': 'MP Edelmetalle',
    'mpedelmetalle.de': 'MP Edelmetalle',
    
    # Weitere Plattformen
    'philoro.de': 'Philoro',
    'bullionvault.com': 'BullionVault',
    'aurinum.de': 'Aurinum',
    
    # Gold.de selbst
    'classic.gold.de': 'Gold.de Classic',
    'cash.gold.de': 'Gold.de Cash',
}

# User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 GoldBot/3.0'
}

def scrape_produkt(name, url):
    """Scrapet ein Produkt mit erweiterter Händlersuche."""
    print(f"   🔍 {name}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"      ⚠️  Status {response.status_code}")
            return None, {}, []
        
        text = response.text.lower()
        
        # Erweiterte Händlersuche
        details = defaultdict(int)
        gefundene_links = []
        
        for pattern, haendler_name in HAENDLER.items():
            pattern_lower = pattern.lower()
            
            # Mehrere Suchmethoden
            count = 0
            
            # 1. Direkter Text-Vergleich
            count += text.count(pattern_lower)
            
            # 2. Suche in URLs (href-Attribute)
            import re
            url_pattern = rf'href=[\'"][^\'"]*{pattern_lower}[^\'"]*[\'"]'
            count += len(re.findall(url_pattern, text))
            
            if count > 0:
                details[haendler_name] = count
                gefundene_links.append(f"{haendler_name}:{count}")
        
        total = sum(details.values())
        
        if total > 0:
            top_haendler = sorted(details.items(), key=lambda x: x[1], reverse=True)[:3]
            haendler_str = ", ".join([f"{h}({c})" for h, c in top_haendler])
            print(f"      ✅ {total} Händler: {haendler_str}")
            
            # Debug: Zeige alle gefundenen Händler
            if len(details) > 3:
                print(f"      📋 Alle: {list(details.keys())}")
        else:
            print(f"      ⏸️  Keine Händler gefunden")
            
            # Debug: Suche nach bekannten Mustern
            debug_patterns = ['heubach', 'esg', 'mp-edelmetalle', 'anlagegold']
            for p in debug_patterns:
                if p in text:
                    print(f"      🔎 '{p}' im Text gefunden!")
        
        return total, dict(details), gefundene_links
        
    except Exception as e:
        print(f"      ❌ Fehler: {str(e)[:80]}")
        return None, {}, []

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
            print(f"✅ Telegram-Nachricht gesendet!")
            return True
        else:
            print(f"❌ Telegram-Fehler: {response_data}")
            return False
            
    except Exception as e:
        print(f"❌ Fehler beim Senden: {e}")
        return False

def erstelle_muenzen_report(ergebnisse):
    """Erstellt speziellen Münzen-Report (stündlich)."""
    muenzen_ergebnisse = [e for e in ergebnisse if e['name'] in MUENZEN]
    
    if not muenzen_ergebnisse:
        return None
    
    # Sortiere nach Anzahl Händler
    muenzen_ergebnisse.sort(key=lambda x: x['count'] if x['count'] is not None else -1, reverse=True)
    
    # Zähle alle Händler für Münzen
    alle_haendler = defaultdict(int)
    for e in muenzen_ergebnisse:
        if e['details']:
            for h, c in e['details'].items():
                alle_haendler[h] += c
    
    # Baue Nachricht
    nachricht = f"<b>🏛️ Aktueller Report - MÜNZEN</b>\n"
    nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    nachricht += f"💰 {len([e for e in muenzen_ergebnisse if e['count'] is not None])}/{len(MUENZEN)} Münzen gescannt\n"
    nachricht += f"🏪 {len(alle_haendler)} verschiedene Händler\n\n"
    
    # TOP 5 Münzen
    nachricht += "<b>🏆 TOP 5 MÜNZEN:</b>\n"
    top_count = 0
    for i, e in enumerate(muenzen_ergebnisse[:5], 1):
        if e['count'] is not None and e['count'] > 0:
            sterne = "★" * min(e['count'], 5)
            nachricht += f"{i}. <b>{e['name']}</b>: {e['count']} Händler {sterne}\n"
            
            if e['details']:
                top_h = sorted(e['details'].items(), key=lambda x: x[1], reverse=True)[:2]
                haendler_str = ", ".join([f"{h}({c})" for h, c in top_h])
                nachricht += f"   <i>{haendler_str}</i>\n"
            
            nachricht += "\n"
            top_count += 1
    
    if top_count == 0:
        nachricht += "<i>Keine Münzen mit Händlern gefunden</i>\n\n"
    
    # Top Händler für Münzen
    if alle_haendler:
        nachricht += "<b>👑 TOP HÄNDLER FÜR MÜNZEN:</b>\n"
        top_haendler = sorted(alle_haendler.items(), key=lambda x: x[1], reverse=True)[:5]
        for h, c in top_haendler:
            nachricht += f"• {h}: <b>{c}</b> Vorkommen\n"
        nachricht += "\n"
    
    # Verfügbarkeits-Statistik
    verfuegbare_muenzen = [e for e in muenzen_ergebnisse if e['count'] and e['count'] > 0]
    if verfuegbare_muenzen:
        nachricht += f"<b>📊 STATISTIK:</b>\n"
        nachricht += f"• Verfügbare Münzen: {len(verfuegbare_muenzen)}/{len(MUENZEN)}\n"
        
        if muenzen_ergebnisse:
            highest = muenzen_ergebnisse[0]
            nachricht += f"• Beste Verfügbarkeit: {highest['name']} ({highest['count']} Händler)\n"
        
        gesamt_anzahl = sum(e['count'] or 0 for e in muenzen_ergebnisse)
        nachricht += f"• Gesamt Händlervorkommen: <b>{gesamt_anzahl}</b>\n"
    
    nachricht += f"\n⏳ Nächster Münzen-Report in 1 Stunde\n"
    nachricht += f"⏰ Barren-Report alle 3 Stunden\n"
    nachricht += f"#GoldMünzen #{datetime.now().strftime('%Y%m%d_%H')}"
    
    return nachricht

def erstelle_barren_report(ergebnisse):
    """Erstellt speziellen Barren-Report (alle 3 Stunden)."""
    barren_ergebnisse = [e for e in ergebnisse if e['name'] in BARREN]
    
    if not barren_ergebnisse:
        return None
    
    # Sortiere nach Anzahl Händler
    barren_ergebnisse.sort(key=lambda x: x['count'] if x['count'] is not None else -1, reverse=True)
    
    # Baue Nachricht
    nachricht = f"<b>🏛️ Aktueller Report - BARREN</b>\n"
    nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    nachricht += f"📦 {len([e for e in barren_ergebnisse if e['count'] is not None])}/{len(BARREN)} Barren gescannt\n\n"
    
    # Barren nach Kategorie
    gold_barren = [e for e in barren_ergebnisse if "Gold" in e['name']]
    silber_barren = [e for e in barren_ergebnisse if "Silber" in e['name']]
    
    if gold_barren:
        nachricht += "<b>🟡 GOLDBARREN:</b>\n"
        for e in gold_barren[:3]:  # Top 3 Goldbarren
            if e['count']:
                nachricht += f"• {e['name']}: {e['count']} Händler\n"
                if e['details']:
                    top_h = list(e['details'].items())[:2]
                    if top_h:
                        nachricht += f"  <i>{top_h[0][0]}({top_h[0][1]})</i>\n"
        nachricht += "\n"
    
    if silber_barren:
        nachricht += "<b>⚪ SILBERBARREN:</b>\n"
        for e in silber_barren[:3]:  # Top 3 Silberbarren
            if e['count']:
                nachricht += f"• {e['name']}: {e['count']} Händler\n"
                if e['details']:
                    top_h = list(e['details'].items())[:2]
                    if top_h:
                        nachricht += f"  <i>{top_h[0][0]}({top_h[0][1]})</i>\n"
        nachricht += "\n"
    
    # Zusammenfassung
    verfuegbare_barren = [e for e in barren_ergebnisse if e['count'] and e['count'] > 0]
    if verfuegbare_barren:
        nachricht += f"<b>📈 ZUSAMMENFASSUNG:</b>\n"
        nachricht += f"• Verfügbare Barren: {len(verfuegbare_barren)}/{len(BARREN)}\n"
        
        if barren_ergebnisse and barren_ergebnisse[0]['count']:
            nachricht += f"• Beliebtester Barren: {barren_ergebnisse[0]['name']}\n"
        
        gesamt_anzahl = sum(e['count'] or 0 for e in barren_ergebnisse)
        nachricht += f"• Gesamt Händlervorkommen: <b>{gesamt_anzahl}</b>\n"
    
    nachricht += f"\n⏳ Nächster Barren-Report in 3 Stunden\n"
    nachricht += f"⏰ Münzen-Report jede Stunde\n"
    nachricht += f"#GoldBarren #{datetime.now().strftime('%Y%m%d')}"
    
    return nachricht

def main():
    """Hauptfunktion."""
    print(f"\n🔍 Starte Scan für {len(PRODUKTE)} Produkte...")
    print("-" * 50)
    
    ergebnisse = []
    
    # Scanne alle Produkte
    for produkt_name, url in PRODUKTE.items():
        count, details, links = scrape_produkt(produkt_name, url)
        ergebnisse.append({
            'name': produkt_name,
            'count': count,
            'details': details,
            'links': links
        })
        sleep(0.5)  # Pause zwischen Requests
    
    print("-" * 50)
    
    # Statistik
    erfolgreich = len([e for e in ergebnisse if e['count'] is not None])
    print(f"📊 {erfolgreich}/{len(PRODUKTE)} Produkte erfolgreich gescannt")
    
    # Bestimme aktuelle Stunde für Logik
    current_hour = datetime.now().hour
    
    # Logik: Münzen immer, Barren nur jede 3. Stunde (0, 3, 6, 9, 12, 15, 18, 21)
    send_muenzen = True  # Münzen immer senden
    send_barren = current_hour % 3 == 0  # Barren nur jede 3. Stunde
    
    print(f"⏰ Stunde: {current_hour}h | Münzen: {'✅' if send_muenzen else '❌'} | Barren: {'✅' if send_barren else '❌'}")
    
    # Reports erstellen und senden
    if send_muenzen:
        muenzen_nachricht = erstelle_muenzen_report(ergebnisse)
        if muenzen_nachricht:
            print(f"\n📤 Sende Münzen-Report...")
            sende_telegram(muenzen_nachricht)
    
    if send_barren:
        barren_nachricht = erstelle_barren_report(ergebnisse)
        if barren_nachricht:
            print(f"\n📤 Sende Barren-Report...")
            sende_telegram(barren_nachricht)
    
    print(f"\n✅ Bot beendet um {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
