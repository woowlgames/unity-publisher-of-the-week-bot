# Unity Asset Store Weekly Scraper

Automated scraper that extracts Unity Asset Store's weekly free asset promotion and posts it to a Telegram channel.

## Features

- 🎁 Automatically scrapes the weekly free asset from Unity's "Publisher of the Week" promotion
- 📝 Extracts asset title, URL, coupon code, and sale end date
- 🏢 Finds publisher URL (including 50% off publisher assets)
- 📱 Sends formatted message to Telegram channel
- ⚙️ GitHub Actions ready for scheduled automation
- 🧪 Test modes for development (`--dry-run` and `--test-message`)

## Prerequisites

- Python 3.7+
- Telegram Bot Token
- Telegram Channel ID

## Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd Telegram
```

2. Create and activate virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

### Telegram Setup

1. **Create a Telegram Bot**:
   - Open Telegram and search for [@BotFather](https://t.me/BotFather)
   - Send `/newbot` and follow the instructions
   - Copy the bot token (e.g., `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ`)

2. **Get Your Channel ID**:
   - Add your bot to your channel as an administrator
   - Send a message in the channel
   - Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Look for `"chat":{"id":-1001234567890,...}` and copy the ID

### Environment Variables

Set the following environment variables:

```bash
# Local development
set TELEGRAM_BOT_TOKEN=your_bot_token_here
set TELEGRAM_CHAT_ID=your_chat_id_here
```

For GitHub Actions, add these as repository secrets (Settings → Secrets → Actions):
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Usage

### Run the Scraper

```bash
# Run normally (sends message to Telegram)
python main.py

# Dry run (preview message without sending)
python main.py --dry-run

# Test with dummy data
python main.py --test-message
```

### GitHub Actions

The scraper can be automated to run weekly using GitHub Actions:

1. Create `.github/workflows/scraper.yml` (if not exists)
2. Configure the schedule (e.g., every Friday at 10:00 AM UTC)
3. Add environment secrets to your repository
4. The workflow will automatically run and post to Telegram

Example workflow schedule:
```yaml
on:
  schedule:
    - cron: '0 10 * * 5'  # Every Friday at 10:00 AM UTC
```

## How It Works

1. **Scrapes the sale page** (`https://assetstore.unity.com/publisher-sale`)
   - Finds the weekly free asset by searching for "coupon code" text
   - Extracts the asset title, coupon code, and sale end date
   - Locates the "Get your gift" button to find the specific asset URL

2. **Fetches the asset page** (e.g., `https://assetstore.unity.com/packages/...`)
   - Makes a second request to get the publisher URL
   - Publisher links are JavaScript-rendered on the sale page, so this workaround is necessary

3. **Formats the message**:
   ```
   Free this week "**Asset Name**" <asset_url>?aid=1011lHuMX
   with the code "COUPONCODE".
   Also, 50% off publisher assets:
   <publisher_url>
   * Sale and related free asset promotion end <date>
   
   Enjoy!!
   ```

4. **Sends to Telegram** using the Bot API

## Example Output

```text
Free this week "**Flexalon Pro: 3D & UI Layouts**" https://assetstore.unity.com/packages/tools/utilities/flexalon-pro-3d-ui-layouts-230509?aid=1011lHuMX
with the code "VIRTUALMAKER".
Also, 50% off publisher assets:
https://assetstore.unity.com/publishers/72095
* Sale and related free asset promotion end November 27, 2025 at 7:59am PT.

Enjoy!!
```

## Limitations

- **Static HTML scraping**: Uses `requests` + `BeautifulSoup`, which works for most content but requires a second request to get the publisher URL
- **Page structure changes**: If Unity Asset Store changes their HTML structure, the scraper may need updates
- **Weekly promotion**: Designed specifically for Unity's "Publisher of the Week" promotion

## Troubleshooting

### "No module named 'requests'"
Make sure you've activated the virtual environment and installed dependencies:
```bash
.\venv\Scripts\activate
pip install -r requirements.txt
```

### "Could not find 'coupon code' keyword"
The page structure may have changed. Run with `--dry-run` to see what's being scraped.

### Telegram message not sending
- Verify your bot token and chat ID are correct
- Ensure the bot is added as an administrator to your channel
- Check that environment variables are set correctly

## Contributing

Feel free to open issues or submit pull requests for improvements!

## License

MIT License - see [LICENSE](LICENSE) file for details.
