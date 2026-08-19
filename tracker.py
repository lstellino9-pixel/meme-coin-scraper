import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import time
from bs4 import BeautifulSoup

# Force immediate log printing in Render console
sys.stdout.reconfigure(line_buffering=True)

# ==========================================
# 1. RENDER PORT BINDING (HEALTH CHECK)
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Scraper active 24/7")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return  # Silence server logs

def run_server():
    port = int(os.environ.get("PORT", 10000))
    HTTPServer(("0.0.0.0", port), HealthCheckHandler).serve_forever()

threading.Thread(target=run_server, daemon=True).start()

# ==========================================
# 2. NTFY ALERT CONFIGURATION
# ==========================================
NTFY_URL = "https://ntfy.sh/luca_meme_alerts"

def send_alert(message):
    try:
        res = requests.post(NTFY_URL, data=message.encode('utf-8'), timeout=10)
        print(f"--- NTFY SUCCESS ({res.status_code}): {message} ---")
    except Exception as e:
        print(f"--- NTFY ERROR: {e} ---")

# Send startup confirmation payload
time.sleep(2)
send_alert("🚀 Scraper active! Monitoring target accounts for $XST and meme coin calls.")

# ==========================================
# 3. SCRAPER CONFIGURATION & TARGETS
# ==========================================
# Keywords to flag in public feeds
KEYWORDS = [
    "$XST", "XST", "money XST", "buying XST", 
    "buy XST", "pump", "solana launch", "ca:"
]

# RSS/Nitter mirrors and public feed endpoints for target accounts
# Note: Replaced direct x.com routes with open web endpoints to bypass login walls
TARGET_FEEDS = [
    "https://nitter.net/pumpdotfun",
    "https://nitter.net/solana",
    "https://nitter.net/dexscreener",
    "https://nitter.net/raydiumprotocol",
    "https://nitter.net/birdeye_so",
    "https://nitter.net/coingecko"
]

seen_matches = set()

# ==========================================
# 4. MAIN SCRAPING LOOP
# ==========================================
while True:
    print("--- Cycle started: Scanning target feeds ---")
    
    for feed_url in TARGET_FEEDS:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            res = requests.get(feed_url, headers=headers, timeout=10)
            
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                page_text = soup.get_text()
                
                for kw in KEYWORDS:
                    if kw.lower() in page_text.lower():
                        match_id = f"{feed_url}_{kw}"
                        
                        if match_id not in seen_matches:
                            alert_body = f"🔥 MEME COIN MATCH: '{kw}' spotted on {feed_url}"
                            send_alert(alert_body)
                            seen_matches.add(match_id)
            else:
                print(f"Feed error {res.status_code} on {feed_url}")
                
        except Exception as err:
            print(f"Scraping exception on {feed_url}: {err}")
            
    # Sleep 60 seconds before next scan iteration
    time.sleep(60)
