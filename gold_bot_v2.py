#!/usr/bin/env python3
"""
Gold.de Verfügbarkeits-Bot - ULTIMATIVE VERSION
Mit Top-Links und verbesserter Händlererkennung
"""

import requests
import os
import sys
import re
from datetime import datetime
from time import sleep
from collections import defaultdict

print("=" * 60)
print("🚀 Gold.de Verfügbarkeits-Bot - ULTIMATIVE VERSION")
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
print("=" * 60)

# Telegram Secrets
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ Telegram Secrets fehlen!")
    sys.exit(1)

# === OPTIMIERTE PRODUKTLISTE ===
MUENZEN = {
    # GOLDMÜNZEN 1oz
    "Krügerrand 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/kruegerrand/",
    "Maple Leaf 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/maple-leaf/",
    "Wiener Philharmoniker 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/philharmoniker/",
    "American Eagle 1oz Gold": "https://www.gold.de/kaufen/goldmuenzen/american-eagle/",
    
    # GOLDMÜNZEN 1/2oz
    "Gold-Euro 1/2oz": "https://www.gold.de/kaufen/goldmuenzen/euro-goldmuenzen/",
    
    # SILBERMÜNZEN 1oz
    "Krügerrand 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/kruegerrand-silber/",
    "Maple Leaf 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/maple-leaf/",
    "Wiener Philharmoniker 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/philharmoniker/",
    
    # SILBERMÜNZEN 10oz
    "Arche Noah 10oz Silber": "https://www.gold.de/kaufen/silbermuenzen/arche-noah/",
}

BARREN = {
    # GOLDBARREN
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "5g Goldbarren": "https://www.gold.de/kaufen/goldbarren/5-gramm/",
    "1oz Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-unze/",
    
    # SILBERBARREN  
    "1oz Silberbarren": "https://www.gold.de/kaufen/silberbarren/1-unze/",
    "50g Silberbarren": "https://www.gold.de/kaufen/silberbarren/50-gramm/",
    "100g Silberbarren": "https://www.gold.de/kaufen/silberbarren/100-gramm/",
}

# WICHTIGE PRODUKTE FÜR TOP-LINKS
TOP_PRODUKTE = {
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "1oz Silberbarren": "https://www.gold.de/kaufen/silberbarren/1-unze/",
    "Wiener Philharmoniker 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/philharmoniker/"
}

PRODUKTE = {**MUENZEN, **BARREN}

# === EXTREM ERWEITERTE HÄNDLERLISTE ===
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
    ('muenze-oesterreich.at', 'Münze Österreich'),
    ('mp-edelmetalle.de', 'MP Edelmetalle'),
    ('mpedelmetalle.de', 'MP Edelmetalle'),
    ('bullionvault.com', 'BullionVault'),
    ('aurinum.de', 'Aurinum'),
    ('coinsinvest.com', 'CoinsInvest'),
    ('coininvest.com', 'CoinInvest'),
    ('silverbroker.de', 'Silverbroker.de'),
    ('edelmetall-handel.de', 'Edelmetall-Handel'),
    ('geld.de', 'Geld.de'),
    ('geldhaus.de', 'Geldhaus'),
    ('smaulgold.com', 'Smaulgold'),
    
    # Text-basierte Händlernamen (werden im HTML-Text gesucht)
    ('göbel', 'GÖBEL Münzen'),
    ('scheidestätte', 'Rheinische Scheidestätte'),
    ('bellmann', 'Bellmann Münzen'),
    ('wasserthal', 'Wasserthal RareCoin'),
    ('rheinmetall', 'Rheinmetall'),
    ('scheideanstalt', 'Scheideanstalt'),
    ('westfälische', 'Westfälische Scheideanstalt'),
    ('bremer', 'Bremer Edelmetall'),
    ('hanseatische', 'Hanseatische Scheideanstalt'),
    ('deutsche', 'Deutsche Edelmetall'),
    ('europäische', 'Europäische Edelmetall'),
    ('österreichische', 'Österreichische Münze'),
    ('liechtensteinische', 'Liechtensteinische Landesbank'),
    ('zürcher', 'Zürcher Kantonalbank'),
    ('ubs', 'UBS'),
    ('degussa', 'Degussa'),  # doppelt für bessere Erkennung
    ('aurum', 'Aurum'),
    ('aurumina', 'Aurumina'),
    
    # Shop-Systeme von Gold.de
    ('classic.gold.de', 'Gold.de Classic'),
    ('cash.gold.de', 'Gold.de Cash'),
    ('shop.gold.de', 'Gold.de Shop'),
]

# User-Agent
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36 GoldBot/4.0'
}

def scrape_produkt(name, url):
    """Scrapet ein Produkt mit AGGRESSIVER Händlersuche."""
    print(f"   🔍 {name}")
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        
        if response.status_code != 200:
            print(f"      ⚠️  Status {response.status_code}")
            return None, {}
        
        text = response.text.lower()
        
        # EXTREM AGGRESSIVE Suche nach Händlern
        details = defaultdict(int)
        
        # Methode 1: Suche in ALLEN href-Links
        href_pattern = r'href=[\'"]([^\'"]*)[\'"]'
        links = re.findall(href_pattern, text)
        
        for link in links:
            link_lower = link.lower()
            for domain, haendler_name in HAENDLER_SUCHWOERTER:
                if domain in link_lower:
                    details[haendler_name] += 1
                    break
        
        # Methode 2: Suche im gesamten HTML-Text
        for suchwort, haendler_name in HAENDLER_SUCHWOERTER:
            suchwort_lower = suchwort.lower()
            if suchwort_lower in text:
                # Zähle alle Vorkommen
                count = text.count(suchwort_lower)
                details[haendler_name] += min(count, 5)  # Max 5 pro Suchwort
        
        # Methode 3: Spezielle Suche nach Shop-Namen in DIVs/SPANs
        shop_patterns = [
            (r'<div[^>]*class=[^>]*shop[^>]*>([^<]*)</div>', 'div.shop'),
            (r'<span[^>]*class=[^>]*händler[^>]*>([^<]*)</span>', 'span.händler'),
            (r'<a[^>]*class=[^>]*dealer[^>]*>([^<]*)</a>', 'a.dealer'),
            (r'<td[^>]*class=[^>]*seller[^>]*>([^<]*)</td>', 'td.seller'),
        ]
        
        for pattern, pattern_name in shop_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                match_lower = match.lower()
                for _, haendler_name in HAENDLER_SUCHWOERTER:
                    if any(word in match_lower for word in haendler_name.lower().split()):
                        details[haendler_name] += 1
        
        total = sum(details.values())
        
        if total > 0:
            # Sortiere und zeige Top Händler
            top_haendler = sorted(details.items(), key=lambda x: x[1], reverse=True)
            haendler_liste = [f"{h}" for h, _ in top_haendler[:8]]
            print(f"      ✅ {len(details)} Händler erkannt")
            
            # Detaillierte Debug-Ausgabe
            if len(top_haendler) <= 10:
                print(f"      📋 Alle: {dict(top_haendler)}")
            else:
                print(f"      📋 Top 10: {dict(top_haendler[:10])}")
        else:
            print(f"      ⏸️  Keine Händler erkannt")
            
            # Debug: Zeige HTML-Ausschnitt
            snippet = text[:500].replace('\n', ' ').replace('\r', ' ')
            print(f"      🔎 HTML-Ausschnitt: {snippet[:200]}...")
        
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

def erstelle_muenzen_report(ergebnisse):
    """Erstellt speziellen Münzen-Report (stündlich)."""
    muenzen_ergebnisse = [e for e in ergebnisse if e['name'] in MUENZEN]
    
    if not muenzen_ergebnisse:
        return None
    
    # Filtere erfolgreiche Scans
    erfolgreiche_muenzen = [e for e in muenzen_ergebnisse if e['count'] is not None]
    erfolgreiche_muenzen.sort(key=lambda x: x['count'] or 0, reverse=True)
    
    if not erfolgreiche_muenzen:
        return "<b>🏛️ Aktueller Report - MÜNZEN</b>\n⚠️ Keine Münzen konnten gescannt werden"
    
    # Zähle Händler
    alle_haendler = defaultdict(int)
    for e in erfolgreiche_muenzen:
        for h, c in e['details'].items():
            alle_haendler[h] += c
    
    # Baue Nachricht
    nachricht = f"<b>🏛️ Aktueller Report - MÜNZEN</b>\n"
    nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    nachricht += f"💰 {len(erfolgreiche_muenzen)}/{len(MUENZEN)} Münzen gescannt\n"
    nachricht += f"🏪 {len(alle_haendler)} verschiedene Händler\n\n"
    
    # TOP Münzen
    verfuegbare_muenzen = [e for e in erfolgreiche_muenzen if e['count'] and e['count'] > 0]
    
    if verfuegbare_muenzen:
        nachricht += "<b>🏆 TOP MÜNZEN:</b>\n"
        for i, e in enumerate(verfuegbare_muenzen[:6], 1):
            sterne = "★" * min(e['count'], 5)
            nachricht += f"{i}. <b>{e['name']}</b>: {e['count']} Händler {sterne}\n"
            
            # Zeige Top 2 Händler
            if e['details']:
                top_h = sorted(e['details'].items(), key=lambda x: x[1], reverse=True)[:2]
                if top_h:
                    haendler_str = ", ".join([f"{h}" for h, _ in top_h])
                    nachricht += f"   <i>{haendler_str}</i>\n"
            
            nachricht += "\n"
    else:
        nachricht += "<i>⚠️ Derzeit keine Münzen bei Händlern verfügbar</i>\n\n"
    
    # Top Händler
    if alle_haendler:
        nachricht += "<b>👑 TOP HÄNDLER:</b>\n"
        top_haendler = sorted(alle_haendler.items(), key=lambda x: x[1], reverse=True)[:8]
        for h, c in top_haendler:
            nachricht += f"• {h}: <b>{c}</b> Angebot"
            if c > 1:
                nachricht += "e"
            nachricht += "\n"
        nachricht += "\n"
    
    # Statistik
    gesamt_anzahl = sum(e['count'] or 0 for e in erfolgreiche_muenzen)
    verfuegbare = len([e for e in erfolgreiche_muenzen if e['count'] and e['count'] > 0])
    
    nachricht += f"<b>📊 STATISTIK:</b>\n"
    nachricht += f"• Verfügbare Münzen: {verfuegbare}/{len(erfolgreiche_muenzen)}\n"
    
    if verfuegbare_muenzen:
        beste = verfuegbare_muenzen[0]
        nachricht += f"• Beste Verfügbarkeit: {beste['name']} ({beste['count']} Händler)\n"
    
    nachricht += f"• Gesamt Angebote: <b>{gesamt_anzahl}</b>\n"
    
    # TOP-PRODUKTE LINKS (gemäß deiner Vorgabe)
    nachricht += f"\n<b>🔗 WICHTIGE PRODUKTE:</b>\n"
    for produkt_name, url in TOP_PRODUKTE.items():
        nachricht += f"• {produkt_name}:\n  {url}\n"
    
    nachricht += f"\n⏳ Nächster Münzen-Report in 1 Stunde\n"
    nachricht += f"#GoldMünzen #{datetime.now().strftime('%Y%m%d_%H')}"
    
    return nachricht

def erstelle_barren_report(ergebnisse):
    """Erstellt speziellen Barren-Report (alle 3 Stunden)."""
    barren_ergebnisse = [e for e in ergebnisse if e['name'] in BARREN]
    
    if not barren_ergebnisse:
        return None
    
    # Filtere erfolgreiche Scans
    erfolgreiche_barren = [e for e in barren_ergebnisse if e['count'] is not None]
    erfolgreiche_barren.sort(key=lambda x: x['count'] or 0, reverse=True)
    
    if not erfolgreiche_barren:
        return "<b>🏛️ Aktueller Report - BARREN</b>\n⚠️ Keine Barren konnten gescannt werden"
    
    # Baue Nachricht
    nachricht = f"<b>🏛️ Aktueller Report - BARREN</b>\n"
    nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
    nachricht += f"📦 {len(erfolgreiche_barren)}/{len(BARREN)} Barren gescannt\n\n"
    
    # Nach Kategorie
    gold_barren = [e for e in erfolgreiche_barren if "Gold" in e['name']]
    silber_barren = [e for e in erfolgreiche_barren if "Silber" in e['name']]
    
    verfuegbare_gold = [e for e in gold_barren if e['count'] and e['count'] > 0]
    verfuegbare_silber = [e for e in silber_barren if e['count'] and e['count'] > 0]
    
    if verfuegbare_gold:
        nachricht += "<b>🟡 GOLDBARREN:</b>\n"
        for e in verfuegbare_gold[:3]:
            nachricht += f"• {e['name']}: {e['count']} Händler\n"
            if e['details']:
                top_h = list(e['details'].items())[:1]
                if top_h:
                    nachricht += f"  <i>{top_h[0][0]}</i>\n"
        nachricht += "\n"
    
    if verfuegbare_silber:
        nachricht += "<b>⚪ SILBERBARREN:</b>\n"
        for e in verfuegbare_silber[:3]:
            nachricht += f"• {e['name']}: {e['count']} Händler\n"
            if e['details']:
                top_h = list(e['details'].items())[:1]
                if top_h:
                    nachricht += f"  <i>{top_h[0][0]}</i>\n"
        nachricht += "\n"
    
    # Statistik
    gesamt_anzahl = sum(e['count'] or 0 for e in erfolgreiche_barren)
    verfuegbare = len([e for e in erfolgreiche_barren if e['count'] and e['count'] > 0])
    
    if verfuegbare > 0:
        nachricht += f"<b>📈 ZUSAMMENFASSUNG:</b>\n"
        nachricht += f"• Verfügbare Barren: {verfuegbare}/{len(erfolgreiche_barren)}\n"
        
        if erfolgreiche_barren and erfolgreiche_barren[0]['count']:
            nachricht += f"• Beliebtester: {erfolgreiche_barren[0]['name']}\n"
        
        nachricht += f"• Gesamt Angebote: <b>{gesamt_anzahl}</b>\n"
    
    nachricht += f"\n⏳ Nächster Barren-Report in 3 Stunden\n"
    nachricht += f"#GoldBarren #{datetime.now().strftime('%Y%m%d')}"
    
    return nachricht

def main():
    """Hauptfunktion."""
    print(f"\n🔍 Starte Scan für {len(PRODUKTE)} Produkte...")
    print("-" * 50)
    
    ergebnisse = []
    
    # Scanne alle Produkte
    for produkt_name, url in PRODUKTE.items():
        count, details = scrape_produkt(produkt_name, url)
        ergebnisse.append({
            'name': produkt_name,
            'count': count,
            'details': details
        })
        sleep(1.5)  # Längere Pause für bessere Erkennung
    
    print("-" * 50)
    
    # Statistik
    erfolgreich = len([e for e in ergebnisse if e['count'] is not None])
    print(f"📊 {erfolgreich}/{len(PRODUKTE)} Produkte erfolgreich gescannt")
    
    # Report-Zeitpunkt
    current_hour = datetime.now().hour
    current_minute = datetime.now().minute
    
    send_muenzen = True
    send_barren = current_hour % 3 == 0 and current_minute < 10
    
    print(f"⏰ Zeit: {current_hour:02d}:{current_minute:02d}")
    print(f"📨 Münzen-Report: {'✅ SENDEN' if send_muenzen else '❌ ÜBERSPRINGEN'}")
    print(f"📦 Barren-Report: {'✅ SENDEN' if send_barren else '❌ ÜBERSPRINGEN'}")
    
    # Reports erstellen und senden
    reports_gesendet = 0
    
    if send_muenzen:
        muenzen_nachricht = erstelle_muenzen_report(ergebnisse)
        if muenzen_nachricht and len(muenzen_nachricht) > 50:
            print(f"\n📤 Sende Münzen-Report ({len(muenzen_nachricht)} Zeichen)...")
            if sende_telegram(muenzen_nachricht):
                reports_gesendet += 1
    
    if send_barren:
        barren_nachricht = erstelle_barren_report(ergebnisse)
        if barren_nachricht and len(barren_nachricht) > 50:
            print(f"\n📤 Sende Barren-Report ({len(barren_nachricht)} Zeichen)...")
            if sende_telegram(barren_nachricht):
                reports_gesendet += 1
    
    print(f"\n✅ Bot beendet um {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
