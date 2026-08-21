# Fake News Detector for Students 🔍

A Python CLI tool that analyses any online news article or pasted text for credibility using AI (OpenAI GPT or Google Gemini). Designed to help students identify misinformation and sharpen their media-literacy skills.

---

## Features

| Feature | Details |
|---|---|
| **URL analysis** | Paste any article URL — the tool fetches and parses the content automatically |
| **Text analysis** | Paste raw article text directly via `--text` or pipe via `--stdin` |
| **Dual LLM support** | Switch between **OpenAI** (GPT-4o-mini) and **Google Gemini** (1.5-flash) |
| **Credibility score** | 0–100 visual bar with a colour-coded verdict |
| **Red flags** | Specific reasons the article may be misleading |
| **Claim fact-check** | Key claims assessed as SUPPORTED / UNSUPPORTED / UNVERIFIABLE |
| **Student tip** | One actionable media-literacy takeaway per article |
| **JSON export** | Save the full structured report with `--json-out report.json` |

---

## Quick Start

### Option A — One-click setup (recommended)

```bat
:: Windows — double-click setup.bat, or run in a terminal:
setup.bat
```

```bash
# macOS / Linux
bash setup.sh
```

The script will:
1. Check that Python 3.10+ is available
2. Create an isolated `venv/` folder so **nothing touches your global Python**
3. Install all required packages into the venv
4. Copy `.env.example` → `.env` (if `.env` doesn't exist yet)

Then add your API key to `.env` and you're done.

---

### Option B — Manual setup

```bash
# 1. Create the virtual environment
python -m venv venv

# 2. Activate it
#    Windows:
venv\Scripts\activate
#    macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env
copy .env.example .env   # Windows
cp .env.example .env     # macOS/Linux
# → open .env and fill in your key
```

Get a **free** Gemini key at <https://aistudio.google.com/app/apikey>
Get an OpenAI key at <https://platform.openai.com/api-keys>

---

### Run

Always activate the venv first, or use the `run.bat` shortcut on Windows:

```bat
:: Windows shortcut (activates venv automatically):
run.bat --url https://www.bbc.com/news/articles/example --provider gemini
run.bat --text "Breaking news: ..." --provider openai

:: Or activate manually first:
venv\Scripts\activate
python detect.py --url https://... --provider gemini
```

```bash
# macOS / Linux
source venv/bin/activate
python detect.py --url https://www.bbc.com/news/articles/example --provider gemini
python detect.py --text "Breaking news: Scientists claim chocolate cures cancer..." --provider gemini
cat my_article.txt | python detect.py --stdin --provider gemini
python detect.py --url https://... --provider openai --json-out report.json
```

---

## CLI Reference

```
usage: detect [-h] (--url URL | --text TEXT | --stdin)
              [--provider {openai,gemini}]
              [--api-key KEY] [--model MODEL]
              [--json-out FILE] [--no-colour]

Options:
  --url, -u URL         URL of the news article to analyse
  --text, -t TEXT       Raw article text (wrap in quotes)
  --stdin               Read article text from standard input
  --provider, -p        LLM provider: openai or gemini (default: gemini)
  --api-key, -k KEY     Override the API key from .env
  --model, -m MODEL     Override the model (e.g. gpt-4o, gemini-1.5-pro)
  --json-out FILE       Save full JSON report to FILE
  --no-colour           Disable coloured output
```

---

## Report Structure

```
═══════════════════════════════════════════════════════════════════════
  🔍  FAKE NEWS DETECTOR — CREDIBILITY REPORT
═══════════════════════════════════════════════════════════════════════

Article:  <title>
Source:   <url>

Credibility Score:
  ████████████░░░░░░░░  62/100

Verdict:  LIKELY_CREDIBLE

───────────────────────────────────────────────────────────────────────
SUMMARY
───────────────────────────────────────────────────────────────────────
<2-3 sentence plain-English summary>

⚠  RED FLAGS
  • Sensational headline not supported by body text
  • No named sources cited

✔  POSITIVE INDICATORS
  • References peer-reviewed research
  • Author byline present

CLAIM-BY-CLAIM FACT CHECK
  Claim:       "X causes Y"
  Assessment:  SUPPORTED
  Details:     Multiple studies confirm this link.

RECOMMENDED VERIFICATION SOURCES
  → https://factcheck.org
  → Reuters Fact Check

💡 STUDENT TIP
  Always check whether the headline matches what the article actually says.
═══════════════════════════════════════════════════════════════════════
```

---

## Project Structure

```
Fake_News/
├── detect.py                    ← CLI entry point
├── requirements.txt
├── .env.example                 ← copy to .env and add your key
└── fake_news_detector/
    ├── __init__.py
    ├── fetcher.py               ← URL scraping & text extraction
    ├── providers.py             ← OpenAI & Gemini wrappers
    ├── analyzer.py              ← prompt engine & JSON parsing
    └── formatter.py             ← coloured terminal output
```

---

## Credibility Scale

| Score | Verdict | Meaning |
|---|---|---|
| 80–100 | ✅ CREDIBLE | Well-sourced, factual |
| 60–79 | 🟢 LIKELY_CREDIBLE | Mostly reliable with minor gaps |
| 40–59 | 🟡 UNCERTAIN | Mixed signals — verify independently |
| 20–39 | 🔴 LIKELY_FAKE | Several red flags detected |
| 0–19 | ❌ FAKE | Strong indicators of misinformation |

---

## Requirements

- Python 3.10+
- `openai` or `google-generativeai` (only the one you use needs an API key)
- `requests`, `beautifulsoup4`, `lxml`, `colorama`, `python-dotenv`
