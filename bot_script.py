import requests
import re
import os
from datetime import datetime

print("🚀 Gold.de Verfügbarkeits-Bot startet...")
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")

# === KONFIGURATION ===
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    print("❌ FEHLER: TELEGRAM_TOKEN oder TELEGRAM_CHAT_ID nicht gesetzt!")
    print("   Bitte in GitHub Repository → Settings → Secrets anlegen.")
    exit(1)

# Liste der 15 PRODUKTE
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

# Suchmuster für Händler
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
]

def scrape_verfuegbarkeit(produkt_name, url):
    """Ruft die Produktseite ab und zählt Händler-Vorkommen."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (GitHub-Actions-Bot/1.0; +https://github.com/your-repo)'
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        html_text = response.text
        gesamt_count = 0
        
        for pattern in SUCHMUSTER:
            matches = re.findall(pattern, html_text, re.IGNORECASE)
            gesamt_count += len(matches)
        
        print(f"   ✅ {produkt_name}: {gesamt_count} Händlervorkommen")
        return gesamt_count
        
    except Exception as e:
        print(f"   ❌ {produkt_name}: Fehler - {str(e)[:50]}")
        return None

def sende_telegram(nachricht):
    """Sendet Telegram-Nachricht."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': nachricht,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(url, json=data, timeout=10)
        return response.json().get('ok', False)
    except:
        return False

def main():
    print(f"\n🔍 Scanne {len(PRODUKTE)} Produkte...")
    
    ergebnisse = []
    for produkt_name, url in PRODUKTE.items():
        anzahl = scrape_verfuegbarkeit(produkt_name, url)
        if anzahl is not None:
            ergebnisse.append(f"{produkt_name}: {anzahl}")
    
    # Zusammenfassung erstellen
    if ergebnisse:
        zusammenfassung = (
            f"🏦 Gold.de Verfügbarkeits-Check\n"
            f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            f"📊 Gescannt: {len(ergebnisse)}/{len(PRODUKTE)} Produkte\n\n"
            f"Top 3 nach Händlervorkommen:\n"
        )
        
        # Sortiere nach Anzahl (nur zur Demonstration)
        top_3 = sorted(ergebnisse, key=lambda x: int(x.split(": ")[1]), reverse=True)[:3]
        for e in top_3:
            zusammenfassung += f"• {e}\n"
        
        zusammenfassung += f"\n🔄 Nächster Check in 4 Stunden"
        
        # Sende Nachricht
        if sende_telegram(zusammenfassung):
            print("✅ Telegram-Nachricht gesendet!")
        else:
            print("❌ Fehler beim Senden der Telegram-Nachricht")
    
    print(f"\n✅ Bot abgeschlossen um {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()
