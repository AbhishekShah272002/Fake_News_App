@echo off
:: ============================================================
:: setup.bat — One-click environment setup for Fake News Detector
:: Run this ONCE after cloning the project.
:: ============================================================

echo.
echo  [1/4] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found. Download it from https://python.org
    pause & exit /b 1
)
python --version

echo.
echo  [2/4] Creating virtual environment in .\venv ...
if exist venv (
    echo  venv already exists, skipping creation.
) else (
    python -m venv venv
    if errorlevel 1 ( echo  ERROR creating venv & pause & exit /b 1 )
    echo  venv created.
)

echo.
echo  [3/4] Installing dependencies into venv...
call venv\Scripts\pip.exe install --upgrade pip --quiet
call venv\Scripts\pip.exe install -r requirements.txt
if errorlevel 1 ( echo  ERROR installing packages & pause & exit /b 1 )

echo.
echo  [4/4] Setting up .env file...
if not exist .env (
    copy .env.example .env >nul
    echo  .env created from template.
    echo.
    echo  ACTION REQUIRED: Open .env and add your API key:
    echo    GEMINI_API_KEY=AIza...    ^(free at https://aistudio.google.com/app/apikey^)
    echo    OPENAI_API_KEY=sk-...     ^(at https://platform.openai.com/api-keys^)
) else (
    echo  .env already exists, skipping.
)

echo.
echo ============================================================
echo  Setup complete!
echo.
echo  To activate the environment:
echo    venv\Scripts\activate
echo.
echo  Then run the detector:
echo    python detect.py --url https://... --provider gemini
echo    python detect.py --text "article text here" --provider openai
echo ============================================================
echo.
pause
