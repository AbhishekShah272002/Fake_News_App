"""
fetcher.py — Retrieve article text from a URL or accept raw text directly.
"""
from __future__ import annotations

import re
import textwrap
from typing import Optional

import requests
from bs4 import BeautifulSoup

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0 Safari/537.36"
    )
}
_MAX_CHARS = 12_000  # keep prompts within a sensible token budget


def fetch_from_url(url: str, timeout: int = 15) -> tuple[str, str]:
    """
    Download a web page and extract its main body text.

    Returns
    -------
    (title, body_text)
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not fetch URL: {exc}") from exc

    soup = BeautifulSoup(resp.text, "lxml")

    # Remove noise tags
    for tag in soup(["script", "style", "nav", "footer", "header", "aside", "ads"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else "Unknown Title"

    # Prefer <article> content; fall back to <body>
    container = soup.find("article") or soup.find("body") or soup
    paragraphs = container.find_all(["p", "h1", "h2", "h3"])
    body = "\n".join(p.get_text(separator=" ", strip=True) for p in paragraphs)

    # Collapse excess whitespace
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    body = textwrap.shorten(body, width=_MAX_CHARS, placeholder=" [truncated]")

    return title, body


def prepare_text(raw: str) -> tuple[str, str]:
    """
    Accept raw article text pasted by the user.

    Returns
    -------
    ("Pasted Article", cleaned_text)
    """
    cleaned = re.sub(r"\n{3,}", "\n\n", raw.strip())
    cleaned = textwrap.shorten(cleaned, width=_MAX_CHARS, placeholder=" [truncated]")
    return "Pasted Article", cleaned
