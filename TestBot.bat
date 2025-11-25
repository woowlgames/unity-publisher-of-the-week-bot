@echo off
REM TestBot.bat - Run Unity Asset Scraper with custom parameters
REM Usage: TestBot.bat <BOT_TOKEN> <CHAT_ID> [--test-message|--dry-run]

REM Check if parameters are provided
if "%~1"=="" (
    echo Error: TELEGRAM_BOT_TOKEN is required
    echo Usage: TestBot.bat ^<BOT_TOKEN^> ^<CHAT_ID^> [--test-message^|--dry-run]
    echo Example: TestBot.bat "123456:ABC-DEF" "-1001234567890" --test-message
    exit /b 1
)

if "%~2"=="" (
    echo Error: TELEGRAM_CHAT_ID is required
    echo Usage: TestBot.bat ^<BOT_TOKEN^> ^<CHAT_ID^> [--test-message^|--dry-run]
    echo Example: TestBot.bat "123456:ABC-DEF" "-1001234567890" --test-message
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Set environment variables from parameters
set TELEGRAM_BOT_TOKEN=%~1
set TELEGRAM_CHAT_ID=%~2

REM Run the script with optional flag
echo Running script...
if "%~3"=="" (
    python main.py
) else (
    python main.py %~3
)

echo Done!