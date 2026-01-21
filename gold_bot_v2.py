#!/usr/bin/env python3
"""
Gold.de Verfügbarkeits-Bot - ULTIMATE VERSION v2.1
Mit korrekten Edelmetallpreisen (MetalpriceAPI), 3-Stunden-Rotation
"""

import requests
import os
import sys
import re
from datetime import datetime
from time import sleep
from collections import defaultdict

print("=" * 60)
print("🚀 Gold.de Verfügbarkeits-Bot - ULTIMATE VERSION v2.1")
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
print("=" * 60)

# Telegram Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
METALPRICEAPI_KEY = os.getenv('METALPRICEAPI_KEY')  # 👈 NEU: API-Key

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram Secrets fehlen!")
    sys.exit(1)

# === KORRIGIERTE PRODUKTLISTE ===
PRIORITAET_1 = {
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "Krügerrand 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/kruegerrand-silber/",
    "Maple Leaf 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/maple-leaf/",
    "Wiener Philharmoniker 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/wiener-philharmoniker/",
    "Arche Noah 10oz Silber": "https://www.gold.de/kaufen/silbermuenzen/arche-noah/",
}

GOLDMUENZEN = {
    "Krügerrand 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/kruegerrand/",
    "Maple Leaf 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/maple-leaf/",
    "Wiener Philharmoniker 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/wiener-philharmoniker/",
    "American Eagle 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/american-eagle/",
    "Gold-Euro 1/2oz": "https://www.gold.de/kaufen/goldmuenzen/euro-goldmuenzen/",
}

BARREN = {
    "5g Goldbarren": "https://www.gold.de/kaufen/goldbarren/5-gramm/",
    "1oz Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-unze/",
    "1oz Silberbarren": "https://www.gold.de/kaufen/silberbarren/1-oz/",
    "50g Silberbarren": "https://www.gold.de/kaufen/silberbarren/50-gramm/",
    "100g Silberbarren": "https://www.gold.de/kaufen/silberbarren/100-gramm/",
}

TOP_PRODUKTE = {
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "1oz Silberbarren": "https://www.gold.de/kaufen/silberbarren/1-oz/",
    "Wiener Philharmoniker 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/wiener-philharmoniker/"
}

# === ERWEITERTE HÄNDLERLISTE ===
HAENDLER_SUCHWOERTER = [
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
    ('göbel', 'GÖBEL Münzen'),
    ('scheidestätte', 'Rheinische Scheidestätte'),
    ('bellmann', 'Bellmann Münzen'),
    ('wasserthal', 'Wasserthal RareCoin'),
    ('deutsche edelmetall', 'Deutsche Edelmetall'),
    ('europäische edelmetall', 'Europäische Edelmetall'),
    ('aurum', 'Aurum'),
    ('classic.gold.de', 'Gold.de Classic'),
    ('cash.gold.de', 'Gold.de Cash'),
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 GoldBot/4.0'
}

def get_metal_prices():
    """Holt aktuelle Gold- und Silberpreise von MetalpriceAPI."""
    print("💰 Hole aktuelle Edelmetallpreise...")
    
    if not METALPRICEAPI_KEY:
        print("⚠️  METALPRICEAPI_KEY nicht gesetzt! Verwende Fallback-Preise.")
        return get_fallback_prices()
    
    try:
        # MetalpriceAPI erwartet: 1 Unze Gold (XAU) in EUR umgerechnet
        # Die API gibt zurück: wie viel EUR für 1 Unze Gold
        gold_url = f"https://api.metalpriceapi.com/v1/latest?api_key={METALPRICEAPI_KEY}&base=XAU&currencies=EUR"
        silver_url = f"https://api.metalpriceapi.com/v1/latest?api_key={METALPRICEAPI_KEY}&base=XAG&currencies=EUR"
        
        gold_response = requests.get(gold_url, timeout=15)
        silver_response = requests.get(silver_url, timeout=15)
        
        print(f"📡 Gold API Status: {gold_response.status_code}")
        print(f"📡 Silber API Status: {silver_response.status_code}")
        
        if gold_response.status_code == 200 and silver_response.status_code == 200:
            gold_data = gold_response.json()
            silver_data = silver_response.json()
            
            print(f"📊 Gold API Response: {gold_data}")
            print(f"📊 Silber API Response: {silver_data}")
            
            # MetalpriceAPI gibt den Wert von 1 Unze Metall in EUR zurück
            # Beispiel: {"success":true,"timestamp":1737446400,"date":"2025-01-21","base":"XAU","rates":{"EUR":0.00058}}
            # Das bedeutet: 1 EUR = 0.00058 Unzen Gold → 1 Unze Gold = 1 / 0.00058 = ~1724 EUR
            
            if 'rates' in gold_data and 'EUR' in gold_data['rates']:
                gold_rate = gold_data['rates']['EUR']
                gold_price_eur_per_oz = 1 / gold_rate if gold_rate > 0 else 2100
            else:
                print("❌ Gold-Rate nicht in API-Response gefunden")
                gold_price_eur_per_oz = 2100
            
            if 'rates' in silver_data and 'EUR' in silver_data['rates']:
                silver_rate = silver_data['rates']['EUR']
                silver_price_eur_per_oz = 1 / silver_rate if silver_rate > 0 else 28
            else:
                print("❌ Silber-Rate nicht in API-Response gefunden")
                silver_price_eur_per_oz = 28
            
            # Umrechnung in verschiedene Einheiten
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
                },
                'timestamp': datetime.now().strftime('%H:%M'),
                'source': 'MetalpriceAPI'
            }
            
            print(f"✅ Gold: {prices['gold']['per_gram']:.2f} €/g (1oz = {prices['gold']['per_ounce']:.2f}€)")
            print(f"✅ Silber: {prices['silver']['per_gram']:.2f} €/g (1oz = {prices['silver']['per_ounce']:.2f}€)")
            return prices
            
    except Exception as e:
        print(f"❌ Fehler beim Abrufen der Edelmetallpreise: {e}")
        import traceback
        traceback.print_exc()
    
    # Fallback falls API nicht verfügbar
    return get_fallback_prices()

def get_fallback_prices():
    """Fallback-Preise für den Fall, dass die API nicht verfügbar ist."""
    print("⚠️  Verwende Fallback-Preise...")
    # Realistischere Fallback-Preise (Januar 2025)
    return {
        'gold': {'per_gram': 67.80, 'per_ounce': 2108.50, 'per_kilo': 67800.00},
        'silver': {'per_gram': 0.92, 'per_ounce': 28.62, 'per_kilo': 920.00},
        'timestamp': datetime.now().strftime('%H:%M'),
        'source': 'Fallback (manuell)'
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
    # Stunde % 3 == 0: PRIORITÄT 1 + GOLDMÜNZEN
    # Stunde % 3 == 1: PRIORITÄT 1 + BARREN
    # Stunde % 3 == 2: NUR PRIORITÄT 1
    
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
    
    erfolgreiche = [e for e in ergebnisse if e['count'] is not None]
    erfolgreiche.sort(key=lambda x: x['count'] or 0, reverse=True)
    
    if not erfolgreiche:
        return f"<b>📊 Aktueller Report - {gruppe}</b>\n⚠️ Alle Scans fehlgeschlagen"
    
    alle_haendler = defaultdict(int)
    for e in erfolgreiche:
        for h, c in e['details'].items():
            alle_haendler[h] += c
    
    # Nachricht mit Preisen
    nachricht = f"<b>📊 AKTUELLER REPORT - {gruppe}</b>\n"
    nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    nachricht += f"💎 Preise ({metal_prices['source']}, {metal_prices['timestamp']}):\n\n"
    
    # Formatierte Edelmetallpreise
    nachricht += "<b>💰 AKTUELLE EDELMETALLPREISE:</b>\n"
    nachricht += f"<b>GOLD:</b> {metal_prices['gold']['per_gram']:.2f} €/g | "
    nachricht += f"{metal_prices['gold']['per_ounce']:.2f} €/oz | "
    nachricht += f"{metal_prices['gold']['per_kilo']:,.0f} €/kg\n"
    
    nachricht += f"<b>SILBER:</b> {metal_prices['silver']['per_gram']:.3f} €/g | "
    nachricht += f"{metal_prices['silver']['per_ounce']:.2f} €/oz | "
    nachricht += f"{metal_prices['silver']['per_kilo']:,.0f} €/kg\n\n"
    
    nachricht += f"📈 {len(erfolgreiche)}/{len(ergebnisse)} Produkte gescannt\n"
    nachricht += f"🏪 {len(alle_haendler)} verschiedene Händler\n\n"
    
    # TOP Produkte
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
    
    # Wichtige Produkte
    nachricht += f"\n<b>🔗 WICHTIGE PRODUKTE:</b>\n"
    for produkt_name, url in TOP_PRODUKTE.items():
        if produkt_name in [e['name'] for e in ergebnisse]:
            nachricht += f"• {produkt_name}:\n  {url}\n"
    
    # Nächster Scan
    current_hour = datetime.now().hour
    naechster_zyklus = (current_hour + 1) % 3
    
    zyklus_namen = {0: "GOLDMÜNZEN", 1: "BARREN", 2: "PRIORITÄT 1"}
    
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
        sleep(2)
    
    print("-" * 50)
    
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
