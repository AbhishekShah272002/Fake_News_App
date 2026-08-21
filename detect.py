"""
detect.py -- CLI entry point for the Fake News Detector.

Usage examples
--------------
  python detect.py --url https://example.com/article --provider gemini
  python detect.py --text "Paste your article here..." --provider openai
  python detect.py --url https://... --provider openai --json-out report.json
"""
from __future__ import annotations

# Suppress noisy SDK warnings before any other imports
import warnings
warnings.filterwarnings("ignore")

import argparse
import json
import sys

from dotenv import load_dotenv

load_dotenv()

from fake_news_detector.analyzer import analyse
from fake_news_detector.fetcher import fetch_from_url, prepare_text
from fake_news_detector.formatter import print_report
from fake_news_detector.providers import get_provider


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="detect",
        description=(
            "Fake News Detector for Students — "
            "analyse an article's credibility using AI."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python detect.py --url https://bbc.com/news/... --provider gemini
  python detect.py --text "Breaking: Scientists discover..." --provider openai
  python detect.py --url https://... --provider openai --api-key sk-...
  python detect.py --url https://... --provider gemini --json-out report.json
        """,
    )

    # Input source (mutually exclusive)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--url", "-u",
        metavar="URL",
        help="URL of the news article to analyse.",
    )
    source.add_argument(
        "--text", "-t",
        metavar="TEXT",
        help="Raw article text to analyse (wrap in quotes or pipe from stdin).",
    )
    source.add_argument(
        "--stdin",
        action="store_true",
        help="Read article text from standard input.",
    )

    # Provider options
    parser.add_argument(
        "--provider", "-p",
        choices=["openai", "gemini"],
        default="gemini",
        help="LLM provider to use (default: gemini).",
    )
    parser.add_argument(
        "--api-key", "-k",
        metavar="KEY",
        dest="api_key",
        default=None,
        help="API key for the chosen provider (overrides .env).",
    )
    parser.add_argument(
        "--model", "-m",
        metavar="MODEL",
        default=None,
        help="Override the model name (e.g. gpt-4o, gemini-1.5-pro).",
    )

    # Output options
    parser.add_argument(
        "--json-out",
        metavar="FILE",
        dest="json_out",
        default=None,
        help="Also save the full report as JSON to FILE.",
    )
    parser.add_argument(
        "--no-colour",
        action="store_true",
        dest="no_colour",
        help="Disable coloured terminal output.",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # ── 1. Fetch / prepare article ──────────────────────────────────────────
    try:
        if args.url:
            print(f"[*] Fetching article from {args.url} ...")
            title, body = fetch_from_url(args.url)
        elif args.stdin:
            print("[*] Reading article from stdin ...")
            raw = sys.stdin.read()
            title, body = prepare_text(raw)
        else:
            title, body = prepare_text(args.text)

        if not body.strip():
            print("[!] No article text could be extracted. Aborting.", file=sys.stderr)
            return 1

        print(f"[*] Article loaded: '{title[:80]}' ({len(body)} chars)")

    except RuntimeError as exc:
        print(f"[!] {exc}", file=sys.stderr)
        return 1

    # ── 2. Initialise LLM provider ──────────────────────────────────────────
    try:
        print(f"[*] Using provider: {args.provider.upper()}")
        provider = get_provider(args.provider, api_key=args.api_key, model=args.model)
    except (ValueError, ImportError) as exc:
        print(f"[!] Provider error: {exc}", file=sys.stderr)
        return 1

    # ── 3. Analyse ──────────────────────────────────────────────────────────
    print("[*] Analysing article credibility ...")
    try:
        report = analyse(
            provider=provider,
            title=title,
            body=body,
            url=args.url if args.url else None,
        )
    except RuntimeError as exc:
        print(f"[!] Analysis failed: {exc}", file=sys.stderr)
        return 1

    # ── 4. Display report ───────────────────────────────────────────────────
    if args.no_colour:
        import colorama
        colorama.deinit()

    print_report(report)

    # ── 5. Optional JSON export ─────────────────────────────────────────────
    if args.json_out:
        import dataclasses
        report_dict = dataclasses.asdict(report)
        with open(args.json_out, "w", encoding="utf-8") as fh:
            json.dump(report_dict, fh, indent=2, ensure_ascii=False)
        print(f"[*] JSON report saved to: {args.json_out}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
