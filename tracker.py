import os
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import time
from bs4 import BeautifulSoup

# Force instant log printing in Render console
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
        return  # Keep Render console logs clean

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Run the health check web server in a background thread
threading.Thread(target=run_health_check_server, daemon=True).start()

# ==========================================
# 2. NTFY CONFIGURATION & ALERT FUNCTION
# ==========================================
NTFY_URL = "https://ntfy.sh/luca_meme_alerts"

def send_alert(message):
    try:
        res = requests.post(NTFY_URL, data=message.encode('utf-8'), timeout=10)
        print(f"--- NTFY ALERT SENT ({res.status_code}): {message} ---")
    except Exception as e:
        print(f"--- NTFY ERROR: {e} ---")

# Send startup notification when container boots
time.sleep(2)
send_alert("🚀 Tracker online! Monitoring $XST and target feeds 24/7 on Render.")

# ==========================================
# 3. SCRAPER & KEYWORD MONITORING LOOP
# ==========================================
# Set your target URLs and keywords
TARGET_KEYWORDS = ["$XST", "XST", "pump", "launch"]
TARGET_URLS = [
    # Add your target endpoint or feed URLs here
    # "https://example.com/feed",
]

seen_posts = set()

while True:
    print("--- Scanning target feeds for $XST ---")
    
    for url in TARGET_URLS:
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text()
                
                for keyword in TARGET_KEYWORDS:
                    if keyword.lower() in page_text.lower():
                        alert_msg = f"🔥 MATCH FOUND! Keyword '{keyword}' detected on {url}"
                        
                        # Prevent duplicate spamming for the same match
                        if alert_msg not in seen_posts:
                            send_alert(alert_msg)
                            seen_posts.add(alert_msg)
            else:
                print(f"Failed to fetch {url}: Status {response.status_code}")

        except Exception as err:
            print(f"Error scraping {url}: {err}")
    
    # Wait 60 seconds between scan cycles
    time.sleep(60)
