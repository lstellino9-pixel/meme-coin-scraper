import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import re
import time

# ==========================================
# 1. RENDER PORT BINDING (GET + HEAD HANDLER)
# ==========================================
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Scraper is online 24/7!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        return  # Silence server logs to keep Render console clean

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

threading.Thread(target=run_health_check_server, daemon=True).start()

# ==========================================
# 2. NTFY ALERT & SCRAPER LOGIC
# ==========================================
NTFY_URL = "https://ntfy.sh/luca_meme_alerts"

def send_notification(message):
    try:
        res = requests.post(NTFY_URL, data=message.encode('utf-8'), timeout=10)
        print(f"Alert status {res.status_code}: {message}")
    except Exception as e:
        print(f"Failed to send notification: {e}")

# Delay slightly so network binding completes before sending first alert
time.sleep(3)
send_notification("Tracker online and monitoring 24/7 on Render!")

while True:
    try:
        print("Scanning target feeds...")
        
        # --- PASTE YOUR ACTUAL SCRAPING LOGIC BELOW ---
        # Example:
        # res = requests.get("https://api.example.com/feed")
        # if "$XST" in res.text:
        #     send_notification("ALERT: $XST detected!")

        time.sleep(60)
    except Exception as e:
        print(f"Error during scan loop: {e}")
        time.sleep(60)
