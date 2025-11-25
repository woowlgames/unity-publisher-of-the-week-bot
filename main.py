import os
import re
import requests
from bs4 import BeautifulSoup
import sys
import random
from datetime import datetime

# --- Configuration ---
# Target URL for the "Publisher of the Week" promotion
# NOTE: This URL is generic. The specific asset is usually dynamically loaded or part of this page.
# If this page is heavily JavaScript-dependent, 'requests' might not see the content.
# In that case, a headless browser like Selenium or Playwright would be needed.
URL = "https://assetstore.unity.com/publisher-sale"

# Random Friday greetings
FRIDAY_GREETINGS = [
    "🎉 Happy Friday! Time to level up your game dev journey!",
    "🌟 It's Friday and Unity Asset Store knows it! Get ready for something awesome!",
    "🚀 Friday vibes incoming! Your weekend game dev adventure starts now!",
    "✨ TGIF! Unity's got a special gift to kickstart your creative weekend!",
    "🎮 Happy Friday, developers! Let's end the week with a bang!",
    "🌈 Friday feels + free assets = Perfect combo for game developers!",
    "💎 It's Friday! Time to add some premium quality to your project!",
    "🎊 Cheers to Friday and free Unity assets! Your project deserves this!",
    "⚡ Friday energy is here! Grab this week's free asset and create magic!",
    "🎁 Happy Friday! Unity's Publisher of the Week is bringing the goods!",
    "🌟 Weekend mode: ACTIVATED! Start it right with this free asset!",
    "🔥 It's Friday! Time to fuel your creative fire with premium assets!",
    "🎯 Friday = Game dev freedom! Here's your weekly treasure!",
    "💫 TGIF, devs! Your weekend project just got a whole lot better!",
    "🏆 Happy Friday! Treat yourself to this week's amazing free asset!",
    "🎨 Friday creativity boost incoming! Unity's got you covered!",
    "🚀 It's Friday! Launch your weekend projects with this free gem!",
    "✨ Happy Friday, creators! Time to make something incredible!",
    "🎮 Weekend warriors, assemble! Here's your Friday power-up!",
    "🌟 It's Friday and your game dev toolkit is about to get richer!"
]

# Telegram Configuration
# These are loaded from Environment Variables (set in GitHub Secrets)
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def scrape_unity_asset():
    """
    Scrapes the Unity Asset Store for the weekly free asset.
    Returns a dictionary with asset details or None if failed.
    """
    print(f"Scraping URL: {URL}")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # --- SCRAPING LOGIC ---
        # NOTE: This part is highly dependent on the current DOM structure of the Unity Asset Store.
        # Since I cannot see the live page structure right now, I am using generic/heuristic selectors
        # based on common patterns (looking for "coupon" or specific classes).
        # YOU MAY NEED TO INSPECT THE PAGE AND UPDATE THESE SELECTORS.
        
        # Heuristic: Look for a container that mentions "coupon code" or "Free"
        # This is a placeholder logic. In a real scenario, we'd inspect the specific class names.
        # Example: looking for a div that contains "Use code"
        
        asset_title = "Unknown Asset"
        asset_url = URL # Default to the sale page if specific asset URL not found
        coupon_code = "Unknown Code"
        publisher_url = URL
        sale_end_date = "Unknown Date"
        
        # Try to find the coupon code section
        # Often text like "Use code: XXXXX"
        # We search for text nodes containing "code" or "coupon"
        found_coupon = False
        
        # Hypothetical traversal - searching for the "Free" section
        # This is a best-effort attempt without live DOM inspection
        for element in soup.find_all(string=True):
            if "coupon code" in element.lower() or "use code" in element.lower():
                parent = element.parent
                # Try to extract the code. It might be in a <strong> or <span> next to it.
                # This is a guess.
                text = parent.get_text(strip=True)
                # Simple extraction logic (might need regex for better precision)
                # New logic: Look for "coupon code" followed by uppercase word
                # The text observed was "... enter the coupon code VIRTUALMAKER at checkout ..."
                match = re.search(r"coupon code\s+([A-Z0-9]+)", text, re.IGNORECASE)
                if match:
                    coupon_code = match.group(1)
                    found_coupon = True
                    # Try to find the asset title nearby
                    # Go up a few levels to find a header?
                    container = parent.find_parent("div")
                    if container:
                        title_tag = container.find("h3") or container.find("h2") or container.find("h1")
                        if title_tag:
                            asset_title = title_tag.get_text(strip=True)
                        # Try to find a link to the asset
                        # 1. Look for link in container with '/packages/'
                        link = container.find("a", href=lambda h: h and "/packages/" in h)
                        # 2. If not found, look for link with title text in the whole soup
                        if not link and asset_title != "Unknown Asset":
                             link = soup.find("a", string=lambda t: t and asset_title in t, href=lambda h: h and "/packages/" in h)
                        # 3. Try to find a 'quick look' or 'product' link nearby
                        if not link:
                             # Look for any link that looks like a product link in the container
                             link = container.find("a", href=lambda h: h and ("/packages/" in h or "/slug/" in h))
                        
                        # 4. User suggestion: Find button with text "Get your gift"
                        if not link:
                            # Search in the whole soup for this specific button/link
                            link = soup.find("a", string=lambda t: t and "Get your gift" in t, href=True)

                        if link:
                            asset_url = link['href']
                            if not asset_url.startswith("http"):
                                asset_url = "https://assetstore.unity.com" + asset_url
                        
                        # Try to find sale end date
                        # User suggested: "* Sale and related free asset promotion end ..."
                        page_text = soup.get_text(" ", strip=True)
                        
                        # Try specific phrase first
                        date_match = re.search(r"Sale and related free asset promotion end\s+(.*?)(?=\.|$)", page_text, re.IGNORECASE)
                        if not date_match:
                             # Fallback
                             date_match = re.search(r"(Sale ends|Ends)[:\s]+(.*?)(?=\.|$|Terms)", page_text, re.IGNORECASE)
                        
                        if date_match:
                            raw_date = date_match.group(1 if date_match.re.groups == 1 else 2).strip()
                            sale_end_date = f"Sale and related free asset promotion end {raw_date}."
                        else:
                            print(f"DEBUG: Could not find date. Page text snippet: {page_text[-500:]}")

                        # Try to find publisher URL
                        # New approach: Make a second request to the asset page and extract publisher link from there
                        # The publisher link should be available in the static HTML of the asset page
                        if asset_url and asset_url != URL:
                            try:
                                asset_response = requests.get(asset_url, headers=headers)
                                asset_response.raise_for_status()
                                asset_soup = BeautifulSoup(asset_response.content, "html.parser")
                                
                                # Look for a link containing "/publishers/"
                                pub_link = asset_soup.find("a", href=lambda h: h and "/publishers/" in h)
                                if pub_link:
                                    publisher_url = pub_link['href']
                                    if not publisher_url.startswith("http"):
                                        publisher_url = "https://assetstore.unity.com" + publisher_url
                            except Exception as e:
                                print(f"Error fetching asset page for publisher URL: {e}")


                break
        
        if not found_coupon:
            print("WARNING: Could not find 'coupon code' keyword in the page. The layout might have changed or is JS-rendered.")
            # Fallback: Print the page title or something to indicate we accessed it
            print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
            return None

        return {
            "name": asset_title,
            "url": asset_url,
            "code": coupon_code,
            "publisher_url": publisher_url, # Might need specific logic to find this
            "end_date": sale_end_date
        }

    except Exception as e:
        print(f"Error during scraping: {e}")
        return None

def format_telegram_message(asset_data):
    """
    Formats the Telegram message with a random Friday greeting.
    Returns the formatted message string.
    """
    # Select a random Friday greeting
    greeting = random.choice(FRIDAY_GREETINGS)
    
    message = (
        f'{greeting}\n\n'
        f'Free this week "<b>{asset_data["name"]}</b>" {asset_data["url"]}?aid=1011lHuMX\n'
        f'with the code "<code>{asset_data["code"]}</code>".\n'
        f'Also, 50% off publisher assets:\n'
        f'{asset_data["publisher_url"]}\n'
        f'• {asset_data["end_date"]}\n\n'
        f'Enjoy!!'
    )
    return message

def send_telegram_message(asset_data):
    """
    Sends a formatted message to the Telegram channel.
    """
    if not BOT_TOKEN or not CHAT_ID:
        print("Error: Telegram credentials not found in environment variables.")
        return

    if not asset_data:
        print("No asset data to send.")
        return

    # Format the message using the helper function
    message = format_telegram_message(asset_data)

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"  # Changed from Markdown to HTML
    }

    try:
        print("Sending Telegram message...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Message sent successfully!")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")
        print(f"Response: {response.text if 'response' in locals() else 'N/A'}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unity Asset Store Scraper")
    parser.add_argument("--dry-run", action="store_true", help="Print message to console instead of sending to Telegram")
    args = parser.parse_args()

    print("Starting Unity Asset Store Scraper...")
    
   
    # 1. Scrape
    asset_data = scrape_unity_asset()
    
    # 2. Send Message or Print
    if asset_data:
        if args.dry_run:
            print("\n--- GENERATED MESSAGE PREVIEW ---")
            # Use the same formatting function
            message = format_telegram_message(asset_data)
            print(message)
            print("---------------------------------")
        else:
            send_telegram_message(asset_data)
    else:
        print("Scraping failed or returned no data. Exiting.")
        sys.exit(1)

if __name__ == "__main__":
    main()
