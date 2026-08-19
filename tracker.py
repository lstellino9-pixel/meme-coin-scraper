import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import time
from bs4 import BeautifulSoup

# Force instant stdout printing in Render logs
sys.stdout.reconfigure(line_buffering=True)

# 1. HEALTH CHECK SERVER FOR RENDER
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")
    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()
    def log_message(self, format, *args):
        return

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# 2. IMMEDIATE TEST ALERT ON BOOT
NTFY_URL = "https://ntfy.sh/luca_meme_alerts"

print("--- BOOTING TRACKER SCRIPT ---")
time.sleep(3)

try:
    res = requests.post(NTFY_URL, data="🚀 Tracker is LIVE and monitoring $XST 24/7!".encode('utf-8'), timeout=10)
    print(f"--- NTFY SUCCESS: CODE {res.status_code} ---")
except Exception as e:
    print(f"--- NTFY FAILED WITH ERROR: {e} ---")

# 3. SCRAPER LOOP
TARGET_KEYWORDS = ["$XST", "XST", "pump"]
TARGET_URLS = []  # Add feed URLs here

seen = set()

while True:
    print("--- Cycle active: Scanning target feeds ---")
    for url in TARGET_URLS:
        try:
            r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                text = soup.get_text()
                for kw in TARGET_KEYWORDS:
                    if kw.lower() in text.lower():
                        msg = f"🔥 MATCH: '{kw}' on {url}"
                        if msg not in seen:
                            requests.post(NTFY_URL, data=msg.encode('utf-8'))
                            seen.add(msg)
        except Exception as err:
            print(f"Scrape error on {url}: {err}")
    time.sleep(60)
