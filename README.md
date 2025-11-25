# Unity Asset Store Weekly Scraper

Automated scraper that extracts Unity Asset Store's weekly free asset promotion and posts it to a Telegram channel.

## Features

- 🎁 Automatically scrapes the weekly free asset from Unity's "Publisher of the Week" promotion
- 📝 Extracts asset title, URL, coupon code, and sale end date
- 🏢 Finds publisher URL (including 50% off publisher assets)
- 📱 Sends formatted message to Telegram channel with random Friday greetings
- 📦 **Historical archive** - Saves all scraped assets to yearly JSON files (assets_archive_2025.json, etc.)
- 🚨 **Error notifications** - Alerts via Telegram when scraping fails
- ⚙️ GitHub Actions ready for scheduled automation
- 🧪 Test modes for development (`--dry-run`)
- 🏗️ **SOLID architecture** - Professional class-based design for maintainability

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

#### Local Development

**Option 1: Set for current PowerShell session (Windows)**
```powershell
# Activate your virtual environment first
.\.venv\Scripts\Activate.ps1

# Set environment variables
$env:TELEGRAM_BOT_TOKEN = "your_bot_token_here"
$env:TELEGRAM_CHAT_ID = "your_chat_id_here"

# Now run the script
python main.py --test-message
```

**Option 2: Set for current CMD session (Windows)**
```cmd
# Activate your virtual environment first
.\.venv\Scripts\activate.bat

# Set environment variables
set TELEGRAM_BOT_TOKEN=your_bot_token_here
set TELEGRAM_CHAT_ID=your_chat_id_here

# Now run the script
python main.py --test-message
```

**Option 3: Set for current Bash session (Linux/Mac)**
```bash
# Activate your virtual environment first
source .venv/bin/activate

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export TELEGRAM_CHAT_ID="your_chat_id_here"

# Now run the script
python main.py --test-message
```

> [!NOTE]
> These environment variables are only set for the current terminal session. You'll need to set them again each time you open a new terminal.

#### GitHub Actions

For GitHub Actions, add these as repository secrets (Settings → Secrets → Actions):
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Usage

### Run the Scraper

#### Using TestBot.bat (Windows - Recommended)

The `TestBot.bat` helper script makes it easy to run the scraper without manually setting environment variables:

```cmd
# Test with dummy data
TestBot.bat "YOUR_BOT_TOKEN" "YOUR_CHAT_ID" --test-message

# Dry run (preview message without sending to Telegram)
TestBot.bat "YOUR_BOT_TOKEN" "YOUR_CHAT_ID" --dry-run

# Run normally (sends message to Telegram)
TestBot.bat "YOUR_BOT_TOKEN" "YOUR_CHAT_ID"
```

**Parameters:**
- **Parameter 1** (required): Your Telegram bot token (e.g., `"123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ"`)
- **Parameter 2** (required): Your Telegram chat ID (e.g., `"-1001234567890"`)
- **Parameter 3** (optional): `--test-message` or `--dry-run`

> [!TIP]
> Using `TestBot.bat` is the easiest way to test on Windows. It automatically activates your virtual environment and sets the credentials for you!

#### Manual Python Execution

```bash
# Run normally (sends message to Telegram)
python main.py

# Dry run (preview message without sending)
python main.py --dry-run

# Test with dummy data
python main.py --test-message
```

> [!NOTE]
> When running manually, make sure you've set the environment variables first (see [Environment Variables](#environment-variables) section).

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
