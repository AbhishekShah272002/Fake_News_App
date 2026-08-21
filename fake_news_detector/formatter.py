"""
formatter.py — Render a CredibilityReport as a rich terminal report.
Uses only ASCII characters for full Windows cp1252 / cmd.exe compatibility.
"""
from __future__ import annotations

import sys

from colorama import Fore, Style, init as colorama_init

from .analyzer import CredibilityReport

# Force UTF-8 output on Windows so Unicode chars print correctly
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf_8"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]
    except Exception:
        pass

colorama_init(autoreset=True)

# Verdict -> colour mapping
_VERDICT_COLOUR = {
    "CREDIBLE":        Fore.GREEN,
    "LIKELY_CREDIBLE": Fore.CYAN,
    "UNCERTAIN":       Fore.YELLOW,
    "LIKELY_FAKE":     Fore.RED,
    "FAKE":            Fore.RED + Style.BRIGHT,
}

_ASSESSMENT_COLOUR = {
    "SUPPORTED":     Fore.GREEN,
    "UNSUPPORTED":   Fore.RED,
    "UNVERIFIABLE":  Fore.YELLOW,
}

_WIDTH = 70


def _hr(char: str = "-") -> str:
    return char * _WIDTH


def _score_bar(score: int) -> str:
    filled = round(score / 5)  # out of 20 blocks
    empty = 20 - filled
    colour = (
        Fore.GREEN if score >= 80
        else Fore.CYAN if score >= 60
        else Fore.YELLOW if score >= 40
        else Fore.RED
    )
    return colour + ("#" * filled) + Style.RESET_ALL + ("." * empty) + f"  {score}/100"


def print_report(report: CredibilityReport) -> None:
    """Print the full credibility report to stdout."""
    vc = _VERDICT_COLOUR.get(report.verdict, Fore.WHITE)

    print()
    print(Style.BRIGHT + "=" * _WIDTH)
    print(Style.BRIGHT + "  [*] FAKE NEWS DETECTOR -- CREDIBILITY REPORT")
    print(Style.BRIGHT + "=" * _WIDTH)

    # Title & source
    print(f"\n{Style.BRIGHT}Article:{Style.RESET_ALL} {report.title}")
    if report.url:
        print(f"{Style.BRIGHT}Source: {Style.RESET_ALL}{report.url}")

    # Score bar & verdict
    print(f"\n{Style.BRIGHT}Credibility Score:{Style.RESET_ALL}")
    print(f"  {_score_bar(report.credibility_score)}")
    print(f"\n{Style.BRIGHT}Verdict:{Style.RESET_ALL} {vc}{Style.BRIGHT}{report.verdict}{Style.RESET_ALL}")

    # Summary
    print(f"\n{Style.BRIGHT}{_hr()}")
    print(f"{Style.BRIGHT}SUMMARY{Style.RESET_ALL}")
    print(_hr())
    print(report.summary)

    # Red flags
    if report.red_flags:
        print(f"\n{Style.BRIGHT}{_hr()}")
        print(f"{Fore.RED}{Style.BRIGHT}[!] RED FLAGS{Style.RESET_ALL}")
        print(_hr())
        for flag in report.red_flags:
            print(f"  {Fore.RED}*{Style.RESET_ALL} {flag}")

    # Positive indicators
    if report.positive_indicators:
        print(f"\n{Style.BRIGHT}{_hr()}")
        print(f"{Fore.GREEN}{Style.BRIGHT}[+] POSITIVE INDICATORS{Style.RESET_ALL}")
        print(_hr())
        for ind in report.positive_indicators:
            print(f"  {Fore.GREEN}+{Style.RESET_ALL} {ind}")

    # Claim checks
    if report.claim_checks:
        print(f"\n{Style.BRIGHT}{_hr()}")
        print(f"{Style.BRIGHT}CLAIM-BY-CLAIM FACT CHECK{Style.RESET_ALL}")
        print(_hr())
        for cc in report.claim_checks:
            ac = _ASSESSMENT_COLOUR.get(cc.assessment, Fore.WHITE)
            print(f"\n  {Style.BRIGHT}Claim:{Style.RESET_ALL} {cc.claim}")
            print(f"  {Style.BRIGHT}Assessment:{Style.RESET_ALL} {ac}{cc.assessment}{Style.RESET_ALL}")
            print(f"  {Style.BRIGHT}Details:{Style.RESET_ALL} {cc.explanation}")

    # Recommended sources
    if report.recommended_sources:
        print(f"\n{Style.BRIGHT}{_hr()}")
        print(f"{Style.BRIGHT}RECOMMENDED VERIFICATION SOURCES{Style.RESET_ALL}")
        print(_hr())
        for src in report.recommended_sources:
            print(f"  {Fore.CYAN}->{Style.RESET_ALL} {src}")

    # Student tip
    if report.student_tip:
        print(f"\n{Style.BRIGHT}{_hr()}")
        print(f"{Fore.CYAN}{Style.BRIGHT}[TIP] STUDENT TIP{Style.RESET_ALL}")
        print(_hr())
        print(f"  {report.student_tip}")

    print(f"\n{Style.BRIGHT}{'=' * _WIDTH}{Style.RESET_ALL}\n")
