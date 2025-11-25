import os
import re
import requests
from bs4 import BeautifulSoup
import sys
import random
from datetime import datetime
from typing import Optional, Dict

# Fix Unicode encoding for Windows console
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


# =============================================================================
# CONFIGURATION CLASS
# =============================================================================

class Config:
    """
    Centralized configuration management (Single Responsibility Principle).
    Validates and provides access to all application settings.
    """
    
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
    
    def __init__(self):
        self.publisher_sale_url = "https://assetstore.unity.com/publisher-sale"
        self.telegram_bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        self.telegram_chat_id = os.environ.get("TELEGRAM_CHAT_ID")
        self.affiliate_id = "1011lHuMX"
        
    def is_telegram_configured(self) -> bool:
        """Check if Telegram credentials are available."""
        return bool(self.telegram_bot_token and self.telegram_chat_id)
    
    def get_random_greeting(self) -> str:
        """Get a random Friday greeting."""
        return random.choice(self.FRIDAY_GREETINGS)


# =============================================================================
# MESSAGE FORMATTER CLASS
# =============================================================================

class MessageFormatter:
    """
    Formats messages for Telegram (Single Responsibility Principle).
    Open for extension, closed for modification (Open/Closed Principle).
    """
    
    def __init__(self, config: Config):
        self.config = config
    
    def format_asset_message(self, asset_data: Dict[str, str]) -> str:
        """Format the weekly asset message."""
        greeting = self.config.get_random_greeting()
        
        message = (
            f'{greeting}\n\n'
            f'Free this week "<b>{asset_data["name"]}</b>" {asset_data["url"]}?aid={self.config.affiliate_id}\n'
            f'with the code "<code>{asset_data["code"]}</code>".\n'
            f'Also, 50% off publisher assets:\n'
            f'{asset_data["publisher_url"]}\n'
            f'{asset_data["end_date"]}\n\n'
            f'Enjoy!!'
        )
        return message
    
    def format_error_message(self, error_type: str, error_details: str, include_timestamp: bool = True) -> str:
        """Format an error notification message."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC") if include_timestamp else ""
        
        error_message = (
            f"🚨 <b>Unity Asset Scraper Error</b>\n\n"
            f"<b>Error Type:</b> {error_type}\n"
            f"<b>Details:</b>\n{error_details}\n\n"
        )
        
        if include_timestamp:
            error_message += f"<i>Time: {timestamp}</i>"
        
        return error_message


# =============================================================================
# ARCHIVE SERVICE CLASS
# =============================================================================

class ArchiveService:
    """
    Manages historical archive of scraped assets (Single Responsibility Principle).
    Saves data to yearly JSON files with automatic rotation.
    """
    
    def __init__(self, config: Config, archive_dir: str = "."):
        self.config = config
        self.archive_dir = archive_dir
    
    def _get_archive_filename(self) -> str:
        """Get the archive filename for the current year."""
        current_year = datetime.now().year
        return f"{self.archive_dir}/assets_archive_{current_year}.json"
    
    def save_asset(self, asset_data: Dict[str, str]) -> bool:
        """
        Save asset data to the yearly archive file.
        Returns True if successful, False otherwise.
        """
        import json
        from pathlib import Path
        
        try:
            archive_file = self._get_archive_filename()
            
            # Load existing data or create new list
            if Path(archive_file).exists():
                with open(archive_file, 'r', encoding='utf-8') as f:
                    archive = json.load(f)
            else:
                archive = []
            
            # Add timestamp to the entry
            entry = {
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "name": asset_data["name"],
                "url": asset_data["url"] + "?aid=" + self.config.affiliate_id,
                "code": asset_data["code"],
                "publisher_url": asset_data["publisher_url"],
                "end_date": asset_data["end_date"]
            }
            
            # Append new entry
            archive.append(entry)
            
            # Save back to file
            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(archive, f, indent=2, ensure_ascii=False)
            
            print(f"📦 Asset archived to {archive_file}")
            return True
            
        except Exception as e:
            print(f"Error saving to archive: {e}")
            return False


# =============================================================================
# ASSET PARSER CLASS
# =============================================================================

class AssetParser:
    """
    Parses HTML content to extract asset information (Single Responsibility Principle).
    """
    
    @staticmethod
    def parse_coupon_code(text: str) -> Optional[str]:
        """Extract coupon code from text."""
        match = re.search(r"coupon code\s+([A-Z0-9]+)", text, re.IGNORECASE)
        return match.group(1) if match else None
    
    @staticmethod
    def parse_sale_end_date(text: str) -> Optional[str]:
        """Extract sale end date from text."""
        # Try specific phrase first
        date_match = re.search(r"Sale and related free asset promotion end\s+(.*?)(?=\.|$)", text, re.IGNORECASE)
        if not date_match:
            # Fallback
            date_match = re.search(r"(Sale ends|Ends)[:\s]+(.*?)(?=\.|$|Terms)", text, re.IGNORECASE)
        
        if date_match:
            raw_date = date_match.group(1 if date_match.re.groups == 1 else 2).strip()
            return f"* Sale and related free asset promotion end {raw_date}."
        return None
    
    @staticmethod
    def find_asset_link(soup: BeautifulSoup, asset_title: str = None) -> Optional[str]:
        """Find the asset URL from the page."""
        # Try to find "Get your gift" button
        link = soup.find("a", string=lambda t: t and "Get your gift" in t, href=True)
        
        # If not found, look for package links
        if not link:
            link = soup.find("a", href=lambda h: h and "/packages/" in h)
        
        if link and link.get('href'):
            url = link['href']
            if not url.startswith("http"):
                url = "https://assetstore.unity.com" + url
            return url
        return None
    
    @staticmethod
    def find_publisher_url(soup: BeautifulSoup) -> Optional[str]:
        """Find the publisher URL from the asset page."""
        pub_link = soup.find("a", href=lambda h: h and "/publishers/" in h)
        if pub_link and pub_link.get('href'):
            url = pub_link['href']
            if not url.startswith("http"):
                url = "https://assetstore.unity.com" + url
            return url
        return None


# =============================================================================
# ASSET SCRAPER CLASS
# =============================================================================

class AssetScraper:
    """
    Handles web scraping operations (Single Responsibility Principle).
    Uses AssetParser for parsing logic (Dependency Inversion Principle).
    """
    
    def __init__(self, config: Config, parser: AssetParser):
        self.config = config
        self.parser = parser
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    
    def _make_request(self, url: str) -> Optional[BeautifulSoup]:
        """Make HTTP request and return BeautifulSoup object."""
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")
            return None
    
    def scrape(self) -> Optional[Dict[str, str]]:
        """
        Scrape the Unity Asset Store for the weekly free asset.
        Returns a dictionary with asset details or None if failed.
        """
        print(f"Scraping URL: {self.config.publisher_sale_url}")
        soup = self._make_request(self.config.publisher_sale_url)
        
        if not soup:
            return None
        
        # Initialize default values
        asset_title = "Unknown Asset"
        asset_url = self.config.publisher_sale_url
        coupon_code = "Unknown Code"
        publisher_url = self.config.publisher_sale_url
        sale_end_date = "Unknown Date"
        
        # Search for coupon code in the page
        found_coupon = False
        for element in soup.find_all(string=True):
            if "coupon code" in element.lower() or "use code" in element.lower():
                parent = element.parent
                text = parent.get_text(strip=True)
                
                # Extract coupon code
                code = self.parser.parse_coupon_code(text)
                if code:
                    coupon_code = code
                    found_coupon = True
                    
                    # Try to find asset title
                    container = parent.find_parent("div")
                    if container:
                        title_tag = container.find("h3") or container.find("h2") or container.find("h1")
                        if title_tag:
                            asset_title = title_tag.get_text(strip=True)
                        
                        # Try to find asset URL
                        link_url = self.parser.find_asset_link(container, asset_title)
                        if not link_url:
                            link_url = self.parser.find_asset_link(soup, asset_title)
                        if link_url:
                            asset_url = link_url
                        
                        # Extract sale end date
                        page_text = soup.get_text(" ", strip=True)
                        end_date = self.parser.parse_sale_end_date(page_text)
                        if end_date:
                            sale_end_date = end_date
                        else:
                            print(f"DEBUG: Could not find date. Page text snippet: {page_text[-500:]}")
                        
                        # Fetch publisher URL from asset page
                        if asset_url and asset_url != self.config.publisher_sale_url:
                            asset_soup = self._make_request(asset_url)
                            if asset_soup:
                                pub_url = self.parser.find_publisher_url(asset_soup)
                                if pub_url:
                                    publisher_url = pub_url
                    
                    break
        
        if not found_coupon:
            print("WARNING: Could not find 'coupon code' keyword in the page. The layout might have changed or is JS-rendered.")
            print(f"Page Title: {soup.title.string if soup.title else 'No Title'}")
            return None
        
        return {
            "name": asset_title,
            "url": asset_url,
            "code": coupon_code,
            "publisher_url": publisher_url,
            "end_date": sale_end_date
        }


# =============================================================================
# TELEGRAM SERVICE CLASS
# =============================================================================

class TelegramService:
    """
    Handles all Telegram communication (Single Responsibility Principle).
    Depends on abstraction (Config) not concretions (Dependency Inversion Principle).
    """
    
    def __init__(self, config: Config, formatter: MessageFormatter):
        self.config = config
        self.formatter = formatter
    
    def _post_to_api(self, message: str) -> bool:
        """Send a message to Telegram API."""
        if not self.config.is_telegram_configured():
            print("Error: Telegram credentials not found in environment variables.")
            return False
        
        url = f"https://api.telegram.org/bot{self.config.telegram_bot_token}/sendMessage"
        payload = {
            "chat_id": self.config.telegram_chat_id,
            "text": message,
            "parse_mode": "HTML"
        }
        
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error posting to Telegram API: {e}")
            print(f"Response: {response.text if 'response' in locals() else 'N/A'}")
            return False
    
    def send_message(self, asset_data: Dict[str, str]) -> bool:
        """Send the weekly asset message."""
        if not asset_data:
            print("No asset data to send.")
            return False
        
        message = self.formatter.format_asset_message(asset_data)
        print("Sending Telegram message...")
        
        if self._post_to_api(message):
            print("Message sent successfully!")
            return True
        else:
            # Send error notification about failed message
            self.send_error_notification(
                "Message Sending Failed",
                "Could not send the weekly asset message.\n\nPlease check Telegram credentials and API response."
            )
            return False
    
    def send_error_notification(self, error_type: str, error_details: str) -> bool:
        """Send an error notification."""
        if not self.config.is_telegram_configured():
            print("Cannot send error notification: Telegram credentials not found.")
            return False
        
        message = self.formatter.format_error_message(error_type, error_details)
        print(f"Sending error notification: {error_type}")
        
        if self._post_to_api(message):
            print("Error notification sent successfully.")
            return True
        else:
            print(f"Failed to send error notification.")
            return False


# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unity Asset Store Scraper")
    parser.add_argument("--dry-run", action="store_true", help="Print message to console instead of sending to Telegram")
    args = parser.parse_args()

    print("Starting Unity Asset Store Scraper...")
    
    # Initialize dependencies (Dependency Injection)
    config = Config()
    asset_parser = AssetParser()
    message_formatter = MessageFormatter(config)
    asset_scraper = AssetScraper(config, asset_parser)
    telegram_service = TelegramService(config, message_formatter)
    archive_service = ArchiveService(config)
    
    # 1. Scrape
    asset_data = asset_scraper.scrape()
    
    # 2. Send Message or Print
    if asset_data:
        # Save to archive first (before sending)
        archive_service.save_asset(asset_data)
        
        if args.dry_run:
            print("\n--- GENERATED MESSAGE PREVIEW ---")
            message = message_formatter.format_asset_message(asset_data)
            print(message)
            print("---------------------------------")
        else:
            telegram_service.send_message(asset_data)
    else:
        error_msg = "Scraping failed or returned no data."
        print(error_msg)
        
        # Send error notification (only in production, not during dry-run)
        if not args.dry_run:
            telegram_service.send_error_notification(
                "Scraping Failed",
                "Could not extract asset data from Unity Asset Store.\n\n"
                "Possible causes:\n"
                "• Page structure has changed\n"
                "• Asset promotion is not active\n"
                "• Network/connectivity issue\n\n"
                "Please check the GitHub Actions logs for details."
            )
        
        sys.exit(1)

if __name__ == "__main__":
    main()
