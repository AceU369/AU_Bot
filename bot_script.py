#!/usr/bin/env python3
"""
Gold.de Verfügbarkeits-Bot
Prüft Produktverfügbarkeit und sendet Telegram-Benachrichtigungen
"""

import requests
import re
import os
import sys
from datetime import datetime
from time import sleep

# === KONFIGURATION ===
print("=" * 60)
print("🚀 Gold.de Verfügbarkeits-Bot startet...")
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
print("=" * 60)

# Telegram Secrets aus GitHub Actions
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Debug: Prüfe ob Secrets gesetzt sind (nicht die Werte ausgeben aus Sicherheit!)
print(f"🔐 Telegram Token vorhanden: {'JA' if TELEGRAM_TOKEN else 'NEIN'}")
print(f"🔐 Telegram Chat-ID vorhanden: {'JA' if TELEGRAM_CHAT_ID else 'NEIN'}")

if not TELEGRAM_TOKEN:
    print("❌ KRITISCH: TELEGRAM_BOT_TOKEN nicht gesetzt!")
    print("   Bitte in GitHub Repository → Settings → Secrets → Actions anlegen:")
    print("   Name: TELEGRAM_BOT_TOKEN")
    print("   Wert: dein_bot_token_von_botfather")
    sys.exit(1)

if not TELEGRAM_CHAT_ID:
    print("❌ KRITISCH: TELEGRAM_CHAT_ID nicht gesetzt!")
    print("   Bitte in GitHub Repository → Settings → Secrets → Actions anlegen:")
    print("   Name: TELEGRAM_CHAT_ID")
    print("   Wert: deine_chat_id (mit /getchatid vom Bot holen)")
    sys.exit(1)

# Liste der PRODUKTE (15 wie gewünscht)
PRODUKTE = {
    "Krügerrand 1 oz": "https://www.gold.de/kaufen/goldmuenzen/kruegerrand/",
    "Maple Leaf 1 oz": "https://www.gold.de/kaufen/goldmuenzen/canadian-maple-leaf/",
    "Gold-Euro 1/2 oz": "https://www.gold.de/kaufen/goldmuenzen/euro-goldmuenzen/",
    "1g Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-gramm/",
    "5g Goldbarren": "https://www.gold.de/kaufen/goldbarren/5-gramm/",
    "1oz Goldbarren": "https://www.gold.de/kaufen/goldbarren/1-unze/",
    "100g Goldbarren": "https://www.gold.de/kaufen/goldbarren/100-gramm/",
    "Maple Leaf 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/canadian-maple-leaf/",
    "Wiener Philharmoniker 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/philharmoniker/",
    "Krügerrand 1oz Silber": "https://www.gold.de/kaufen/silbermuenzen/kruegerrand-silber/",
    "Arche Noah 10oz Silber": "https://www.gold.de/kaufen/silbermuenzen/arche-noah/",
    "1oz Silberbarren": "https://www.gold.de/kaufen/silberbarren/1-unze/",
    "100g Silberbarren": "https://www.gold.de/kaufen/silberbarren/100-gramm/",
    "250g Silberbarren": "https://www.gold.de/kaufen/silberbarren/250-gramm/",
    "500g Silberbarren": "https://www.gold.de/kaufen/silberbarren/500-gramm/"
}

# Suchmuster für Händler (erweiterte Liste)
SUCHMUSTER = [
    r'stonexbullion\.com',
    r'goldsilbershop\.de',
    r'proaurum\.de',
    r'degussa\.de',
    r'heubach\.de',
    r'esesg\.de',
    r'philoro\.de',
    r'classic\.gold\.de',
    r'classic\.silber\.de',
    r'bullionvault\.com',
    r'aurinum\.de',
    r'cash\.gold\.de',
]

# User-Agent für Requests
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

def scrape_verfuegbarkeit(produkt_name, url, versuch=1):
    """
    Ruft die Produktseite ab und zählt Händler-Vorkommen.
    """
    max_versuche = 2
    
    try:
        print(f"   🔍 Scanne: {produkt_name}")
        print(f"      📍 URL: {url}")
        
        # Künstliche Verzögerung um nicht geblockt zu werden
        sleep(1)
        
        response = requests.get(url, headers=HEADERS, timeout=25)
        response.raise_for_status()
        
        # Prüfe ob Seite erreichbar
        if response.status_code != 200:
            print(f"      ⚠️  Status-Code: {response.status_code}")
            if versuch < max_versuche:
                print(f"      🔄 Versuche erneut ({versuch}/{max_versuche})...")
                return scrape_verfuegbarkeit(produkt_name, url, versuch + 1)
            return None
        
        html_text = response.text.lower()  # Kleinschreibung für case-insensitive Suche
        gesamt_count = 0
        gefundene_haendler = []
        
        # Zähle Händler-Vorkommen
        for pattern in SUCHMUSTER:
            matches = re.findall(pattern, html_text)
            anzahl = len(matches)
            if anzahl > 0:
                gesamt_count += anzahl
                haendler_name = pattern.replace(r'\.', '.').replace('\\', '')
                gefundene_haendler.append(f"{haendler_name}: {anzahl}")
        
        print(f"      ✅ Gefunden: {gesamt_count} Händlervorkommen")
        if gefundene_haendler:
            print(f"      📋 Händler: {', '.join(gefundene_haendler[:3])}" + 
                  ("..." if len(gefundene_haendler) > 3 else ""))
        
        return gesamt_count
        
    except requests.exceptions.Timeout:
        print(f"      ❌ Timeout bei {produkt_name}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"      ❌ Netzwerkfehler: {str(e)[:80]}")
        return None
    except Exception as e:
        print(f"      ❌ Unerwarteter Fehler: {str(e)[:80]}")
        return None

def sende_telegram_nachricht(text):
    """
    Sendet eine Nachricht an Telegram.
    Gibt True zurück bei Erfolg, False bei Fehler.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True
    }
    
    try:
        print("\n📤 Sende Telegram-Nachricht...")
        print(f"   📝 Länge: {len(text)} Zeichen")
        
        response = requests.post(url, json=payload, timeout=15)
        response_data = response.json()
        
        if response.status_code == 200 and response_data.get('ok'):
            print(f"   ✅ Telegram-Nachricht erfolgreich gesendet!")
            print(f"   📨 Nachricht-ID: {response_data.get('result', {}).get('message_id', 'unbekannt')}")
            return True
        else:
            print(f"   ❌ Telegram-Fehler {response.status_code}:")
            print(f"      {response_data}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ❌ Timeout bei Telegram-Sendevorgang")
        return False
    except Exception as e:
        print(f"   ❌ Fehler beim Senden an Telegram: {e}")
        return False

def main():
    """
    Hauptfunktion des Bots.
    """
    print(f"\n🔍 Starte Verfügbarkeits-Check für {len(PRODUKTE)} Produkte...")
    print("-" * 50)
    
    ergebnisse = []
    erfolgreiche_scans = 0
    
    # Scanne jedes Produkt
    for produkt_name, url in PRODUKTE.items():
        anzahl = scrape_verfuegbarkeit(produkt_name, url)
        
        if anzahl is not None:
            ergebnisse.append({
                'name': produkt_name,
                'count': anzahl,
                'url': url
            })
            erfolgreiche_scans += 1
        else:
            print(f"   ⚠️  {produkt_name}: Scan fehlgeschlagen")
    
    print("-" * 50)
    print(f"📊 Scan abgeschlossen: {erfolgreiche_scans}/{len(PRODUKTE)} Produkte erfolgreich")
    
    # Erstelle Bericht
    if ergebnisse:
        # Sortiere nach Häufigkeit (absteigend)
        ergebnisse.sort(key=lambda x: x['count'], reverse=True)
        
        # Baue Nachricht zusammen
        nachricht = f"<b>🏦 Gold.de Verfügbarkeits-Report</b>\n"
        nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        nachricht += f"📊 {erfolgreiche_scans}/{len(PRODUKTE)} Produkte gescannt\n"
        nachricht += f"🔍 {len(SUCHMUSTER)} Händler gesucht\n\n"
        
        nachricht += "<b>🏆 Top 5 nach Händlervorkommen:</b>\n"
        for i, ergebnis in enumerate(ergebnisse[:5], 1):
            sterne = "★" * min(ergebnis['count'], 5)  # 1-5 Sterne
            nachricht += f"{i}. {ergebnis['name']}: <b>{ergebnis['count']}</b> {sterne}\n"
        
        nachricht += f"\n<b>📈 Zusammenfassung:</b>\n"
        nachricht += f"• Höchste Verfügbarkeit: {ergebnisse[0]['name']} ({ergebnisse[0]['count']})\n"
        nachricht += f"• Niedrigste Verfügbarkeit: {ergebnisse[-1]['name']} ({ergebnisse[-1]['count']})\n"
        
        gesamt_anzahl = sum(e['count'] for e in ergebnisse)
        nachricht += f"• Gesamt Händlervorkommen: <b>{gesamt_anzahl}</b>\n"
        
        nachricht += f"\n🔄 Nächster Check in 4 Stunden\n"
        nachricht += f"#GoldBot #{datetime.now().strftime('%Y%m%d')}"
        
        # Sende Nachricht
        print("\n" + "=" * 50)
        print("📄 ERSTELLTE NACHRICHT:")
        print("-" * 50)
        print(nachricht.replace('<b>', '').replace('</b>', ''))
        print("=" * 50)
        
        erfolgreich = sende_telegram_nachricht(nachricht)
        
        if erfolgreich:
            print("\n🎉 Bot erfolgreich ausgeführt!")
        else:
            print("\n⚠️  Bot ausgeführt, aber Telegram-Sendung fehlgeschlagen")
    else:
        print("\n❌ Keine Ergebnisse zum Senden - alle Scans fehlgeschlagen")
        nachricht = f"<b>⚠️ Gold.de Verfügbarkeits-Check FEHLER</b>\n"
        nachricht += f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
        nachricht += f"❌ Alle {len(PRODUKTE)} Scans fehlgeschlagen\n"
        nachricht += f"🔧 Bitte Logs prüfen!"
        sende_telegram_nachricht(nachricht)
    
    print(f"\n✅ Bot beendet um {datetime.now().strftime('%H:%M:%S')}")
    print("=" * 60)

# Starte das Programm
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot manuell gestoppt")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ KRITISCHER FEHLER: {e}")
        sys.exit(1)
