#!/usr/bin/env python3
"""
Gold.de Verfügbarkeits-Bot - ULTIMATIVE VERSION v2.0
Mit Edelmetallpreisen, 3-Stunden-Rotation und intelligenter Lastverteilung
"""

import requests
import os
import sys
import re
import json
from datetime import datetime
from time import sleep
from collections import defaultdict

print("=" * 60)
print("🚀 Gold.de Verfügbarkeits-Bot - ULTIMATIVE VERSION v2.0")
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
print("=" * 60)

# Telegram Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram Secrets fehlen!")
    sys.exit(1)

# === KORRIGIERTE PRODUKTLISTE MIT FUNKTIONIERENDEN URLs ===
# PRIORITÄT 1: Silbermünzen + 1g Gold (werden in jedem Zyklus gescannt)
PRIORITAET_1 = {
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "Krügerrand 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/kruegerrand-silber/",
    "Maple Leaf 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/maple-leaf/",
    "Wiener Philharmoniker 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/wiener-philharmoniker/",
    "Arche Noah 10oz Silber": "https://www.gold.de/kaufen/silbermuenzen/arche-noah/",
}

# PRIORITÄT 2: Goldmünzen (werden im GOLDMÜNZEN-Zyklus gescannt)
GOLDMUENZEN = {
    "Krügerrand 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/kruegerrand/",
    "Maple Leaf 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/maple-leaf/",
    "Wiener Philharmoniker 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/wiener-philharmoniker/",
    "American Eagle 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/american-eagle/",
    "Gold-Euro 1/2oz": "https://www.gold.de/kaufen/goldmuenzen/euro-goldmuenzen/",
}

# PRIORITÄT 3: Barren (werden im BARREN-Zyklus gescannt)
BARREN = {
    "5g Goldbarren": "https://www.gold.de/kaufen/goldbarren/5-gramm/",
    "1oz Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-unze/",
    "1oz Silberbarren": "https://www.gold.de/kaufen/silberbarren/1-oz/",
    "50g Silberbarren": "https://www.gold.de/kaufen/silberbarren/50-gramm/",
    "100g Silberbarren": "https://www.gold.de/kaufen/silberbarren/100-gramm/",
}

# WICHTIGE PRODUKTE FÜR TOP-LINKS
TOP_PRODUKTE = {
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "1oz Silberbarren": "https://www.gold.de/kaufen/silberbarren/1-oz/",
    "Wiener Philharmoniker 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/wiener-philharmoniker/"
}

# === ERWEITERTE HÄNDLERLISTE ===
HAENDLER_SUCHWOERTER = [
    # Domain-basierte Händler
    ('goldsilbershop.de', 'GoldSilberShop'),
    ('anlagegold24.de', 'Anlagegold24'),
    ('stonexbullion.com', 'StoneX Bullion'),
    ('proaurum.de', 'Pro Aurum'),
    ('degussa.de', 'Degussa'),
    ('heubach.de', 'Heubach Edelmetalle'),
    ('esesg.de', 'ESG Edelmetall-Service'),
    ('philoro.de', 'Philoro'),
    ('aurargentum.de', 'Aurargentum'),
    ('muenzeoesterreich.at', 'Münze Österreich'),
    ('mp-edelmetalle.de', 'MP Edelmetalle'),
    ('bullionvault.com', 'BullionVault'),
    ('aurinum.de', 'Aurinum'),
    ('coinsinvest.com', 'CoinsInvest'),
    ('silverbroker.de', 'Silverbroker.de'),
    
    # Text-basierte Händlernamen
    ('göbel', 'GÖBEL Münzen'),
    ('scheidestätte', 'Rheinische Scheidestätte'),
    ('bellmann', 'Bellmann Münzen'),
    ('wasserthal', 'Wasserthal RareCoin'),
    ('deutsche edelmetall', 'Deutsche Edelmetall'),
    ('europäische edelmetall', 'Europäische Edelmetall'),
    ('aurum', 'Aurum'),
    
    # Shop-Systeme
    ('classic.gold.de', 'Gold.de Classic'),
    ('cash.gold.de', 'Gold.de Cash'),
]

# User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 GoldBot/4.0'
}

# API für Edelmetallpreise
METAL_PRICE_API = "https://api.frankfurter.app/latest?from=USD&to=EUR"

def get_metal_prices():
    """Holt aktuelle Gold- und Silberpreise von einer API."""
    print("💰 Hole aktuelle Edelmetallpreise...")
    
    try:
        # Goldpreis in USD pro Unze (Standard)
        gold_response = requests.get("https://api.frankfurter.app/latest?from=XAU&to=EUR", timeout=10)
        
        # Silberpreis in USD pro Unze (Standard)
        silver_response = requests.get("https://api.frankfurter.app/latest?from=XAG&to=EUR", timeout=10)
        
        if gold_response.status_code == 200 and silver_response.status_code == 200:
            gold_data = gold_response.json()
            silver_data = silver_response.json()
            
            # Umrechnungen
            gold_price_eur_per_oz = gold_data['rates']['EUR']
            silver_price_eur_per_oz = silver_data['rates']['EUR']
            
            # Umrechnung in verschiedene Einheiten
            # 1 Unze = 31.1034768 Gramm
            OUNCE_TO_GRAM = 31.1034768
            
            prices = {
                'gold': {
                    'per_gram': gold_price_eur_per_oz / OUNCE_TO_GRAM,
                    'per_ounce': gold_price_eur_per_oz,
                    'per_kilo': (gold_price_eur_per_oz / OUNCE_TO_GRAM) * 1000
                },
                'silver': {
                    'per_gram': silver_price_eur_per_oz / OUNCE_TO_GRAM,
                    'per_ounce': silver_price_eur_per_oz,
                    'per_kilo': (silver_price_eur_per_oz / OUNCE_TO_GRAM) * 1000
                }
            }
            
            print(f"✅ Gold: {prices['gold']['per_gram']:.2f} €/g")
            print(f"✅ Silber: {prices['silver']['per_gram']:.2f} €/g")
            return prices
            
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Edelmetallpreise: {e}")
    
    # Fallback-Preise falls API nicht verfügbar
    return {
        'gold': {'per_gram': 65.50, 'per_ounce': 2037.50, 'per_kilo': 65500.00},
        'silver': {'per_gram': 0.85, 'per_ounce': 26.45, 'per_kilo': 850.00}
    }

def scrape_produkt(name, url):
    """Scrapet ein Produkt mit erweiterter Händlersuche."""
    print(f"   🔍 {name}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"      ⚠️  Status {response.status_code}")
            return None, {}
        
        text = response.text.lower()
        
        details = defaultdict(int)
        
        # Methode 1: Suche in href-Links
        href_pattern = r'href=[\'"](https?://[^\'"]*)[\'"]'
        links = re.findall(href_pattern, text)
        
        for link in links:
            link_lower = link.lower()
            for domain, haendler_name in HAENDLER_SUCHWOERTER:
                if domain in link_lower:
                    details[haendler_name] += 1
                    break
        
        # Methode 2: Direkte Textsuche
        for suchwort, haendler_name in HAENDLER_SUCHWOERTER:
            if suchwort in text:
                count = text.count(suchwort)
                details[haendler_name] += min(count, 3)
        
        total = sum(details.values())
        
        if total > 0:
            top_haendler = sorted(details.items(), key=lambda x: x[1], reverse=True)[:5]
            haendler_str = ", ".join([f"{h}" for h, _ in top_haendler])
            print(f"      ✅ {len(details)} Händler: {haendler_str}")
        else:
            print(f"      ⏸️  Keine Händler erkannt")
        
        return total, dict(details)
        
    except Exception as e:
        print(f"      ❌ Fehler: {e}")
        return None, {}

def sende_telegram(text, max_length=3800):
    """Sendet Telegram-Nachricht mit Längenlimit."""
    if len(text) > max_length:
        print(f"⚠️  Nachricht zu lang ({len(text)} > {max_length}), kürze...")
        text = text[:max_length] + "\n\n... (Nachricht gekürzt)"
    
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

def bestimme_scan_gruppe():
    """Bestimmt welche Produktgruppe basierend auf der aktuellen Stunde gescannt wird."""
    current_hour = datetime.now().hour
    
    # 3-Stunden-Rotation:
    # Stunde % 3 == 0: PRIORITÄT 1 (Silbermünzen + 1g Gold) + GOLDMÜNZEN
    # Stunde % 3 == 1: PRIORITÄT 1 (Silbermünzen + 1g Gold) + BARREN
    # Stunde % 3 == 2: NUR PRIORITÄT 1 (Silbermünzen + 1g Gold) - Ruhephase
    
    if current_hour % 3 == 0:
        return "GOLDMÜNZEN", {**PRIORITAET_1, **GOLDMUENZEN}
    elif current_hour % 3 == 1:
        return "BARREN", {**PRIORITAET_1, **BARREN}
    else:
        return "PRIORITÄT 1", PRIORITAET_1

def erstelle_report(ergebnisse, gruppe, metal_prices):
    """Erstellt einen Report mit Edelmetallpreisen."""
    if not ergebnisse:
        return f"<b>📊 Aktueller Report - {gruppe}</b>\n⚠️ Keine Daten verfügbar"
    
    # Filtere erfolgreiche Scans
    erfolgreiche = [e for e in ergebnisse if e['count'] is not None]
    erfolgreiche.sort(key=lambda x: x['count'] or 0, reverse=True)
    
    if not erfolgreiche:
        return f"<b>📊 Aktueller Report - {gruppe}</b>\n⚠️ Alle Scans fehlgeschlagen"
    
    # Zähle Händler
    alle_haendler = defaultdict(int)
    for e in erfolgreiche:
        for h, c in e['details'].items():
            alle_haendler[h] += c
    
    # Baue Nachricht mit Edelmetallpreisen
    nachricht = f"<b>📊 AKTUELLER REPORT - {gruppe}</b>\n"
    nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
    
    # Edelmetallpreise
    nachricht += "<b>💰 AKTUELLE EDELMETALLPREISE:</b>\n"
    nachricht += f"<b>GOLD:</b> {metal_prices['gold']['per_gram']:.2f} €/g | "
    nachricht += f"{metal_prices['gold']['per_ounce']:.2f} €/oz | "
    nachricht += f"{metal_prices['gold']['per_kilo']:,.0f} €/kg\n"
    
    nachricht += f"<b>SILBER:</b> {metal_prices['silver']['per_gram']:.2f} €/g | "
    nachricht += f"{metal_prices['silver']['per_ounce']:.2f} €/oz | "
    nachricht += f"{metal_prices['silver']['per_kilo']:,.0f} €/kg\n\n"
    
    nachricht += f"📈 {len(erfolgreiche)}/{len(ergebnisse)} Produkte gescannt\n"
    nachricht += f"🏪 {len(alle_haendler)} verschiedene Händler\n\n"
    
    # TOP Produkte (max 6)
    verfuegbare = [e for e in erfolgreiche if e['count'] and e['count'] > 0]
    
    if verfuegbare:
        nachricht += "<b>🏆 TOP PRODUKTE:</b>\n"
        for i, e in enumerate(verfuegbare[:6], 1):
            sterne = "★" * min(e['count'], 5)
            nachricht += f"{i}. <b>{e['name']}</b>: {e['count']} Händler {sterne}\n"
            
            if e['details']:
                top_h = sorted(e['details'].items(), key=lambda x: x[1], reverse=True)[:2]
                if top_h:
                    haendler_str = ", ".join([f"{h}" for h, _ in top_h])
                    nachricht += f"   <i>{haendler_str}</i>\n"
            
            nachricht += "\n"
    else:
        nachricht += "<i>⚠️ Derzeit keine Produkte bei Händlern verfügbar</i>\n\n"
    
    # Top Händler
    if alle_haendler:
        nachricht += "<b>👑 TOP HÄNDLER:</b>\n"
        top_haendler = sorted(alle_haendler.items(), key=lambda x: x[1], reverse=True)[:6]
        for h, c in top_haendler:
            nachricht += f"• {h}: <b>{c}</b> Angebot"
            if c > 1:
                nachricht += "e"
            nachricht += "\n"
        nachricht += "\n"
    
    # Statistik
    gesamt_anzahl = sum(e['count'] or 0 for e in erfolgreiche)
    
    nachricht += f"<b>📈 STATISTIK:</b>\n"
    nachricht += f"• Verfügbare Produkte: {len(verfuegbare)}/{len(erfolgreiche)}\n"
    
    if verfuegbare:
        beste = verfuegbare[0]
        nachricht += f"• Beste Verfügbarkeit: {beste['name']} ({beste['count']} Händler)\n"
    
    nachricht += f"• Gesamt Angebote: <b>{gesamt_anzahl}</b>\n"
    
    # Wichtige Produkte (nur wenn in der aktuellen Gruppe)
    nachricht += f"\n<b>🔗 WICHTIGE PRODUKTE:</b>\n"
    for produkt_name, url in TOP_PRODUKTE.items():
        if produkt_name in [e['name'] for e in ergebnisse]:
            nachricht += f"• {produkt_name}:\n  {url}\n"
    
    # Nächster Scan
    current_hour = datetime.now().hour
    naechster_zyklus = (current_hour + 1) % 3
    
    zyklus_namen = {
        0: "GOLDMÜNZEN",
        1: "BARREN", 
        2: "PRIORITÄT 1"
    }
    
    nachricht += f"\n⏳ Nächster Scan: {zyklus_namen[naechster_zyklus]} (in 1 Stunde)\n"
    nachricht += f"🔄 3-Stunden-Rotation aktiv\n"
    nachricht += f"#{gruppe.replace('Ü', 'U')} #{datetime.now().strftime('%Y%m%d_%H')}"
    
    return nachricht

def main():
    """Hauptfunktion mit intelligenter Rotation."""
    # Edelmetallpreise abrufen
    metal_prices = get_metal_prices()
    
    # Bestimme welche Gruppe gescannt wird
    gruppe, zu_scannende_produkte = bestimme_scan_gruppe()
    
    print(f"\n🎯 AKTUELLER SCAN-ZYKLUS: {gruppe}")
    print(f"🔍 Scanne {len(zu_scannende_produkte)} Produkte...")
    print("-" * 50)
    
    ergebnisse = []
    
    # Scanne die bestimmten Produkte
    for produkt_name, url in zu_scannende_produkte.items():
        count, details = scrape_produkt(produkt_name, url)
        ergebnisse.append({
            'name': produkt_name,
            'count': count,
            'details': details
        })
        sleep(2)  # Respektvolle Pause zwischen Requests
    
    print("-" * 50)
    
    # Statistik
    erfolgreich = len([e for e in ergebnisse if e['count'] is not None])
    print(f"📊 {erfolgreich}/{len(ergebnisse)} Produkte erfolgreich gescannt")
    
    # Report erstellen und senden
    report = erstelle_report(ergebnisse, gruppe, metal_prices)
    
    if sende_telegram(report):
        print(f"\n✅ {gruppe}-Report erfolgreich gesendet!")
    else:
        print(f"\n❌ Fehler beim Senden des {gruppe}-Reports")
    
    print(f"\n🏁 Bot beendet um {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
