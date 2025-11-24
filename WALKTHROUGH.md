# Unity Asset Store Scraper Walkthrough

## Summary

Successfully translated the Telegram message from Spanish to English and refined the scraper logic to extract all required data from the Unity Asset Store's weekly promotion.

## Changes Made

### 1. Message Translation
Translated the Telegram notification message from Spanish to English:
- **Before**: "Esta semana gratis..." / "¡¡Disfrutad!!"
- **After**: "Free this week..." / "Enjoy!!"

### 2. Coupon Code Extraction
Implemented regex-based extraction to find uppercase codes following "coupon code":
- Pattern: `r"coupon code\s+([A-Z0-9]+)"`
- Successfully extracts codes like "VIRTUALMAKER"

### 3. Title Formatting
Removed brackets from the title display:
- **Before**: `"**[Flexalon Pro: 3D & UI Layouts]**"`
- **After**: `"**Flexalon Pro: 3D & UI Layouts**"`

### 4. Asset URL Extraction
Improved URL finding by searching for the "Get your gift" button:
- Now correctly finds specific asset URLs like `https://assetstore.unity.com/packages/tools/utilities/flexalon-pro-3d-ui-layouts-230509`

### 5. Sale End Date Extraction
Implemented extraction of the complete sale end date phrase:
- Pattern: `r"Sale and related free asset promotion end\s+(.*?)(?=\.|$)"`
- Output: `"* Sale and related free asset promotion end November 27, 2025 at 7:59am PT."`

### 6. Publisher URL Extraction
Solved the JavaScript-rendered content challenge by making a second request to the asset page:
- **Challenge**: Publisher links not available in static HTML of the sale page
- **Solution**: Fetch the asset page and extract the publisher link from there
- Successfully extracts: `https://assetstore.unity.com/publishers/72095`

## Final Output

```text
Free this week "**Flexalon Pro: 3D & UI Layouts**" https://assetstore.unity.com/packages/tools/utilities/flexalon-pro-3d-ui-layouts-230509?aid=1011lHuMX
with the code "VIRTUALMAKER".
Also, 50% off publisher assets:
https://assetstore.unity.com/publishers/72095
* Sale and related free asset promotion end November 27, 2025 at 7:59am PT.

Enjoy!!
```

## Testing

All features verified using `--dry-run` mode with the virtual environment:
```bash
.\venv\Scripts\python.exe main.py --dry-run
```

The scraper successfully extracts:
✅ Asset Title
✅ Asset URL (specific package)
✅ Coupon Code
✅ Sale End Date
✅ Publisher URL
