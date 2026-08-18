import requests
from bs4 import BeautifulSoup
import re
import time

# -------------------------------------------------------------
# CONFIGURATION
# -------------------------------------------------------------
NTFY_TOPIC = "meme-coin-scraper"

# Accounts to monitor (Added niche crypto accounts)
TARGET_ACCOUNTS = [
    "pumpdotfun", 
    "dexscreener", 
    "solana",
    "raydiumprotocol",
    "cookerbiot",
    "solanakings"
]

# Specific tokens/keywords to watch for
WATCH_KEYWORDS = ["$XST", "XST", "TRUMP", "GEM", "100X", "CA:"]

# Free open-source Twitter mirror instances
NITTER_SERVERS = [
    "https://nitter.poast.org",
    "https://nitter.privacydev.net",
    "https://nitter.lucabased.xyz"
]

seen_tweets = set()

def send_ntfy_alert(account, text, ca_list, tickers):
    url = f"https://ntfy.sh/{NTFY_TOPIC}"
    
    body = f"@{account} posted:\n\n\"{text}\"\n"
    if ca_list:
        body += f"\n🚨 CA: {ca_list[0]}"
    
    headers = {
        "Title": f"Meme Alert: {', '.join(tickers) if tickers else 'New Post'}",
        "Priority": "high",
        "Tags": "rocket,moneybag"
    }
    
    try:
        requests.post(url, data=body.encode('utf-8'), headers=headers)
        print(f"[+] ALERT SENT TO PHONE: @{account}")
    except Exception as e:
        print(f"[-] Failed to send ntfy alert: {e}")

def check_accounts():
    ca_pattern = r'[1-9A-HJ-NP-Za-km-z]{32,44}|0x[a-fA-F0-9]{40}'
    
    for account in TARGET_ACCOUNTS:
        scraped = False
        for instance in NITTER_SERVERS:
            if scraped:
                break
            url = f"{instance}/{account}"
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, "html.parser")
                    tweets = soup.find_all("div", class_="tweet-content")
                    
                    for tweet in tweets:
                        tweet_text = tweet.get_text().strip()
                        tweet_id = f"{account}_{hash(tweet_text)}"
                        
                        if tweet_id not in seen_tweets:
                            seen_tweets.add(tweet_id)
                            found_cas = re.findall(ca_pattern, tweet_text)
                            found_tickers = re.findall(r'\$[A-Za-z]+', tweet_text)
                            
                            # Check for keywords or CAs/tickers
                            has_keyword = any(kw.lower() in tweet_text.lower() for kw in WATCH_KEYWORDS)
                            
                            if found_cas or found_tickers or has_keyword:
                                send_ntfy_alert(account, tweet_text, found_cas, found_tickers)
                    scraped = True
            except Exception:
                continue

if __name__ == "__main__":
    print("🚀 Free Meme Coin Tracker Started! Listening for tweets & $XST...")
    while True:
        try:
            check_accounts()
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nTracker stopped.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(10)