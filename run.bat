@echo off
:: run.bat — Quick launcher that activates the venv and runs detect.py
:: Usage: run.bat --url https://... --provider gemini
::        run.bat --text "article text" --provider openai

call venv\Scripts\activate
python detect.py %*
