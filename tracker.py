import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import time

# --- DUMMY SERVER FOR RENDER PORT BINDING ---
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Meme scraper is live!")

def run_health_check_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Start port listener in a background thread
threading.Thread(target=run_health_check_server, daemon=True).start()

# --- SCRAPER LOGIC ---
NTFY_URL = "https://ntfy.sh/luca_meme_alerts"  # Update this if your ntfy topic name is different

def send_notification(message):
    try:
        requests.post(NTFY_URL, data=message.encode('utf-8'))
    except Exception as e:
        print(f"Failed to send alert: {e}")

print("Scraper starting up...")
send_notification("Render deployment successful! Scraper is now online 24/7.")

while True:
    try:
        print("Scanning for meme coins...")
        time.sleep(60) 
    except Exception as e:
        print(f"Error during scan loop: {e}")
        time.sleep(60)
