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
print("🚀 Gold.de Verfügbarkeits-Bot v2.0 startet...")  # ⭐ HIER STEHT v2.0!
print(f"⏰ {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
print("=" * 60)
