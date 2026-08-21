"""
analyzer.py — Core credibility analysis engine.

Sends the article text to the chosen LLM using a carefully crafted
prompt and parses the structured JSON response into a Python dataclass.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import List

from .providers import LLMProvider

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = """\
You are an expert fact-checker and media-literacy educator helping students \
identify misinformation. Your job is to analyse a news article and return a \
thorough credibility report.

IMPORTANT:
- Be objective and evidence-based.
- Do NOT make up sources; if you cannot verify a claim, say so.
- Keep explanations student-friendly (clear, concise, no jargon).
- ALWAYS respond with valid JSON only — no markdown fences, no extra text.

Return a JSON object with EXACTLY these keys:

{
  "credibility_score": <integer 0-100>,
  "verdict": "<one of: CREDIBLE | LIKELY_CREDIBLE | UNCERTAIN | LIKELY_FAKE | FAKE>",
  "summary": "<2-3 sentence plain-English summary of the article>",
  "red_flags": ["<flag 1>", "<flag 2>", ...],
  "positive_indicators": ["<indicator 1>", ...],
  "claim_checks": [
    {"claim": "<key claim>", "assessment": "<SUPPORTED|UNSUPPORTED|UNVERIFIABLE>", "explanation": "<brief>"},
    ...
  ],
  "recommended_sources": ["<URL or publication name>", ...],
  "student_tip": "<one actionable media-literacy tip related to this article>"
}

credibility_score meaning:
  80-100 → CREDIBLE
  60-79  → LIKELY_CREDIBLE
  40-59  → UNCERTAIN
  20-39  → LIKELY_FAKE
  0-19   → FAKE
"""


def _build_user_prompt(title: str, body: str, url: str | None = None) -> str:
    source_line = f"Source URL: {url}" if url else "Source: (text provided directly)"
    return (
        f"Article title: {title}\n"
        f"{source_line}\n\n"
        f"--- ARTICLE CONTENT START ---\n{body}\n--- ARTICLE CONTENT END ---\n\n"
        "Analyse this article and return the JSON credibility report."
    )


# ---------------------------------------------------------------------------
# Result dataclass
# ---------------------------------------------------------------------------

@dataclass
class ClaimCheck:
    claim: str
    assessment: str   # SUPPORTED | UNSUPPORTED | UNVERIFIABLE
    explanation: str


@dataclass
class CredibilityReport:
    title: str
    url: str | None
    credibility_score: int
    verdict: str
    summary: str
    red_flags: List[str] = field(default_factory=list)
    positive_indicators: List[str] = field(default_factory=list)
    claim_checks: List[ClaimCheck] = field(default_factory=list)
    recommended_sources: List[str] = field(default_factory=list)
    student_tip: str = ""
    raw_response: str = ""


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------

def analyse(
    provider: LLMProvider,
    title: str,
    body: str,
    url: str | None = None,
) -> CredibilityReport:
    """
    Run credibility analysis and return a structured CredibilityReport.
    """
    user_prompt = _build_user_prompt(title, body, url)
    raw = provider.complete(SYSTEM_PROMPT, user_prompt)

    # Strip accidental markdown fences the model might add despite instructions
    clean = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
    clean = re.sub(r"\s*```$", "", clean.strip())

    try:
        data = json.loads(clean)
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"LLM returned non-JSON response. Raw output:\n{raw}\n\nError: {exc}"
        ) from exc

    claim_checks = [
        ClaimCheck(
            claim=c.get("claim", ""),
            assessment=c.get("assessment", "UNVERIFIABLE"),
            explanation=c.get("explanation", ""),
        )
        for c in data.get("claim_checks", [])
    ]

    return CredibilityReport(
        title=title,
        url=url,
        credibility_score=int(data.get("credibility_score", 0)),
        verdict=data.get("verdict", "UNCERTAIN"),
        summary=data.get("summary", ""),
        red_flags=data.get("red_flags", []),
        positive_indicators=data.get("positive_indicators", []),
        claim_checks=claim_checks,
        recommended_sources=data.get("recommended_sources", []),
        student_tip=data.get("student_tip", ""),
        raw_response=raw,
    )
