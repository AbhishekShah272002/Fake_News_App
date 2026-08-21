"""
app.py -- Streamlit web UI for the Fake News Detector.

Run with:
    streamlit run app.py
"""
import warnings
warnings.filterwarnings("ignore")

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from fake_news_detector.fetcher import fetch_from_url, prepare_text
from fake_news_detector.providers import get_provider
from fake_news_detector.analyzer import analyse, CredibilityReport

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Fake News Detector",
    page_icon="🔍",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #f7f8fa; }
    .block-container { padding-top: 2rem; max-width: 780px; }
    .score-bar-wrap { background: #e5e7eb; border-radius: 8px; height: 22px; width: 100%; }
    .score-bar-fill { height: 22px; border-radius: 8px; transition: width 0.4s; }
    .verdict-badge {
        display: inline-block; padding: 4px 16px;
        border-radius: 20px; font-weight: 700; font-size: 1rem;
        margin-top: 6px;
    }
    .card {
        background: #ffffff; border: 1px solid #e5e7eb;
        border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 1rem;
    }
    .flag-item  { color: #dc2626; margin: 4px 0; }
    .good-item  { color: #16a34a; margin: 4px 0; }
    .claim-box  {
        background: #f7f8fa; border-left: 4px solid #3b82d4;
        padding: 8px 12px; border-radius: 4px; margin-bottom: 8px;
    }
    .badge-SUPPORTED    { background:#dcfce7; color:#15803d; }
    .badge-UNSUPPORTED  { background:#fee2e2; color:#b91c1c; }
    .badge-UNVERIFIABLE { background:#fef9c3; color:#92400e; }
    .tip-box {
        background: #eff6ff; border: 1px solid #bfdbfe;
        border-radius: 8px; padding: 0.8rem 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🔍 Fake News Detector")
st.markdown("**AI-powered credibility analysis for students.** Paste a URL or article text and get an instant fact-check report.")
st.divider()

# ── Sidebar — settings ────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Settings")
    provider_choice = st.selectbox(
        "LLM Provider",
        ["gemini", "openai"],
        index=0,
        help="Gemini is free. OpenAI requires credits.",
    )
    api_key_input = st.text_input(
        "API Key (optional)",
        type="password",
        placeholder="Overrides .env file",
        help="Leave blank to use the key from your .env file.",
    )
    model_input = st.text_input(
        "Model override (optional)",
        placeholder="e.g. gemini-flash-lite-latest",
        help="Leave blank to use the default model.",
    )
    st.divider()
    st.markdown("**Credibility Scale**")
    st.markdown("""
    🟢 80–100 &nbsp; CREDIBLE  
    🔵 60–79 &nbsp;&nbsp; LIKELY CREDIBLE  
    🟡 40–59 &nbsp;&nbsp; UNCERTAIN  
    🔴 20–39 &nbsp;&nbsp; LIKELY FAKE  
    ⛔ 0–19 &nbsp;&nbsp;&nbsp; FAKE  
    """)
    st.divider()
    st.caption("Get a free Gemini key → [aistudio.google.com](https://aistudio.google.com/app/apikey)")

# ── Input section ─────────────────────────────────────────────────────────────
input_mode = st.radio(
    "Input type",
    ["🔗  URL", "📝  Paste Text"],
    horizontal=True,
    label_visibility="collapsed",
)

url_input = text_input = ""

if input_mode == "🔗  URL":
    url_input = st.text_input(
        "Article URL",
        placeholder="https://www.bbc.com/news/articles/...",
    )
else:
    text_input = st.text_area(
        "Article Text",
        placeholder="Paste the full article text here...",
        height=200,
    )

analyse_btn = st.button("🔍  Analyse Article", type="primary", use_container_width=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _score_colour(score: int) -> str:
    if score >= 80: return "#16a34a"
    if score >= 60: return "#0ea5e9"
    if score >= 40: return "#eab308"
    return "#dc2626"

def _verdict_colours(verdict: str) -> tuple[str, str]:
    """Returns (background, text) CSS colours."""
    return {
        "CREDIBLE":        ("#dcfce7", "#15803d"),
        "LIKELY_CREDIBLE": ("#e0f2fe", "#075985"),
        "UNCERTAIN":       ("#fef9c3", "#854d0e"),
        "LIKELY_FAKE":     ("#fee2e2", "#b91c1c"),
        "FAKE":            ("#fca5a5", "#7f1d1d"),
    }.get(verdict, ("#f3f4f6", "#374151"))

def render_report(report: CredibilityReport) -> None:
    st.divider()
    st.subheader("📋 Credibility Report")

    # ── Score bar ──────────────────────────────────────────────────────────
    score = report.credibility_score
    colour = _score_colour(score)
    bg, fg = _verdict_colours(report.verdict)

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div class="score-bar-wrap">
          <div class="score-bar-fill" style="width:{score}%; background:{colour}"></div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"**{score} / 100**")

    st.markdown(
        f'<span class="verdict-badge" style="background:{bg}; color:{fg};">'
        f'{report.verdict.replace("_", " ")}</span>',
        unsafe_allow_html=True,
    )

    # ── Article info ───────────────────────────────────────────────────────
    st.markdown(f"**Article:** {report.title}")
    if report.url:
        st.markdown(f"**Source:** {report.url}")

    st.markdown("---")

    # ── Summary ────────────────────────────────────────────────────────────
    with st.expander("📄 Summary", expanded=True):
        st.write(report.summary)

    # ── Red flags ──────────────────────────────────────────────────────────
    if report.red_flags:
        with st.expander(f"⚠️ Red Flags ({len(report.red_flags)})", expanded=True):
            for flag in report.red_flags:
                st.markdown(f'<p class="flag-item">🚩 {flag}</p>', unsafe_allow_html=True)

    # ── Positive indicators ────────────────────────────────────────────────
    if report.positive_indicators:
        with st.expander(f"✅ Positive Indicators ({len(report.positive_indicators)})", expanded=True):
            for ind in report.positive_indicators:
                st.markdown(f'<p class="good-item">✔ {ind}</p>', unsafe_allow_html=True)

    # ── Claim checks ───────────────────────────────────────────────────────
    if report.claim_checks:
        with st.expander(f"🔎 Claim-by-Claim Fact Check ({len(report.claim_checks)} claims)", expanded=True):
            for cc in report.claim_checks:
                badge_cls = f"badge-{cc.assessment}"
                st.markdown(f"""
                <div class="claim-box">
                  <strong>Claim:</strong> {cc.claim}<br>
                  <span class="verdict-badge {badge_cls}" style="font-size:0.8rem; padding:2px 10px;">
                    {cc.assessment}
                  </span><br>
                  <small>{cc.explanation}</small>
                </div>
                """, unsafe_allow_html=True)

    # ── Recommended sources ────────────────────────────────────────────────
    if report.recommended_sources:
        with st.expander("🌐 Recommended Verification Sources"):
            for src in report.recommended_sources:
                st.markdown(f"- {src}")

    # ── Student tip ────────────────────────────────────────────────────────
    if report.student_tip:
        st.markdown(f"""
        <div class="tip-box">
          💡 <strong>Student Tip:</strong> {report.student_tip}
        </div>
        """, unsafe_allow_html=True)

# ── Run analysis ──────────────────────────────────────────────────────────────
if analyse_btn:
    if not url_input.strip() and not text_input.strip():
        st.warning("Please enter a URL or paste article text first.")
    else:
        # Fetch content
        with st.spinner("Fetching article..."):
            try:
                if url_input.strip():
                    title, body = fetch_from_url(url_input.strip())
                else:
                    title, body = prepare_text(text_input.strip())
            except RuntimeError as exc:
                st.error(f"Could not fetch article: {exc}")
                st.stop()

        st.info(f"Loaded: **{title[:80]}** ({len(body)} characters)")

        # Run LLM analysis
        with st.spinner(f"Analysing with {provider_choice.upper()} ..."):
            try:
                provider = get_provider(
                    provider_choice,
                    api_key=api_key_input.strip() or None,
                    model=model_input.strip() or None,
                )
                report = analyse(provider, title, body, url=url_input.strip() or None)
            except (ValueError, RuntimeError) as exc:
                st.error(f"Analysis failed: {exc}")
                st.stop()

        render_report(report)
