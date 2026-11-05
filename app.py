import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st

PROJECT_DIR = Path(__file__).resolve().parent

SCANNER_RESULTS_FILE = (
    PROJECT_DIR / "data" / "results.json"
)

AI_RESULTS_FILE = (
    PROJECT_DIR
    / "person2_ai_module"
    / "data"
    / "ai_analysis_results.json"
)

st.set_page_config(
    page_title="WebDoc | AI Accessibility Doctor",
    page_icon="W",
    layout="wide",
    initial_sidebar_state="collapsed",
)


HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)([A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}$"
)


def normalise_url(raw):
    candidate = raw.strip()
    if not candidate or any(ch.isspace() for ch in candidate):
        return None

    if "://" not in candidate:

        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", candidate) and not re.match(
            r"^[^/]+:\d+(/|$)", candidate
        ):
            return None
        candidate = "https://" + candidate

    try:
        parsed = urlparse(candidate)
        hostname = parsed.hostname
        parsed.port
    except ValueError:
        return None

    if parsed.scheme not in ("http", "https") or not hostname:
        return None
    if parsed.username or parsed.password:
        return None
    if not HOSTNAME_RE.match(hostname):
        return None
    return candidate
def run_full_scan(url):
    """Run website accessibility scan followed by Gemini analysis."""

    ai_module_dir = PROJECT_DIR / "person2_ai_module"
    scanner_results = PROJECT_DIR / "data" / "results.json"

    # Step 1: Run Playwright + axe-core scanner.
    scanner_code = (
        "import sys; "
        "from scanner.scanner import scan_website; "
        "scan_website(sys.argv[1])"
    )

    try:
        scanner_process = subprocess.run(
            [
                sys.executable,
                "-c",
                scanner_code,
                url,
            ],
            cwd=str(PROJECT_DIR),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=180,
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError("Website scanning timed out after 180 seconds.")

    if scanner_process.returncode != 0:
        raise RuntimeError(
            "Accessibility scanner failed:\n"
            + scanner_process.stderr[-4000:]
        )

    if not scanner_results.exists():
        raise RuntimeError("Scanner did not generate results.json.")

    # Step 2: Run Gemini analysis on fresh scanner results.
    ai_script = ai_module_dir / "run_scan_analysis.py"

    try:
        ai_process = subprocess.run(
            [
                sys.executable,
                str(ai_script),
            ],
            cwd=str(ai_module_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=600,
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError("AI analysis timed out after 600 seconds.")

    if ai_process.returncode != 0:
        raise RuntimeError(
            "Gemini analysis pipeline failed:\n"
            + ai_process.stderr[-4000:]
        )

    if not AI_RESULTS_FILE.exists():
        raise RuntimeError("AI analysis JSON was not generated.")

    # Step 3: Load fresh results.
    with scanner_results.open("r", encoding="utf-8") as file:
        scan_data = json.load(file)

    with AI_RESULTS_FILE.open("r", encoding="utf-8") as file:
        ai_data = json.load(file)

    return {
        "scan": scan_data,
        "ai": ai_data,
        "scanner_log": scanner_process.stdout,
        "ai_log": ai_process.stdout,
    }


if "wd_dark_mode" not in st.session_state:
    st.session_state.wd_dark_mode = False
if "wd_page" not in st.session_state:
    st.session_state.wd_page = "Home"
if "wd_url" not in st.session_state:
    st.session_state.wd_url = ""


if "wd_goto" in st.session_state:
    st.session_state.wd_page = st.session_state.pop("wd_goto")


brand_col, nav_col, theme_col = st.columns([1.25, 4.4, 1.15], vertical_alignment="center")
with brand_col:
    st.html(
        """
        <div class="wd-brand">
          <div class="wd-logo">W</div>
          <div><div class="wd-brand-name">WebDoc</div>
          <div class="wd-brand-subtitle">ACCESSIBILITY INTELLIGENCE</div></div>
        </div>
        """
    )

PAGES = ["Home", "Dashboard", "WCAG Issues", "Profiles", "Heatmap", "AI Co-Pilot", "Preview", "Journey"]
with nav_col:
    selected_page = st.radio(
        "Main navigation",
        PAGES,
        horizontal=True,
        key="wd_page",
        label_visibility="collapsed",
    )
with theme_col:
    st.toggle("Dark mode", key="wd_dark_mode")


DARK = st.session_state.wd_dark_mode
if DARK:
    C = {
        "bg": "#100D14", "surface": "#1D1722", "surface2": "#241B2B",
        "primary": "#492D55", "accent": "#EA8DB8", "text": "#F5EFF7",
        "muted": "#B9AABD", "soft": "#302337", "border": "#3A3040",
        "input": "#17111C", "button_text": "#241725", "button": "#EA8DB8",
        "visual1": "#492D55", "visual2": "#24162B", "glow": "rgba(234,141,184,.16)",
        "success": "#86D5B0", "warning": "#F2C078", "danger": "#F08C91"
    }
else:
    C = {
        "bg": "#F4F8FC", "surface": "#FFFFFF", "surface2": "#EAF3FA",
        "primary": "#173F60", "accent": "#F17F73", "text": "#18334B",
        "muted": "#647C91", "soft": "#EAF3FA", "border": "#D7E4EF",
        "input": "#FFFFFF", "button_text": "#FFFFFF", "button": "#173F60",
        "visual1": "#173F60", "visual2": "#102C43", "glow": "rgba(59,130,180,.14)",
        "success": "#237C5A", "warning": "#A96818", "danger": "#BD424B"
    }


CSS = """
<style>
:root {
 --wd-bg: __BG__; --wd-surface: __SURFACE__; --wd-surface2: __SURFACE2__;
 --wd-primary: __PRIMARY__; --wd-accent: __ACCENT__; --wd-text: __TEXT__;
 --wd-muted: __MUTED__; --wd-soft: __SOFT__; --wd-border: __BORDER__;
 --wd-input: __INPUT__; --wd-button-text: __BUTTON_TEXT__; --wd-button: __BUTTON__;
 --wd-visual1: __VISUAL1__; --wd-visual2: __VISUAL2__; --wd-glow: __GLOW__;
 --wd-success: __SUCCESS__; --wd-warning: __WARNING__; --wd-danger: __DANGER__;
}
html { scroll-behavior: smooth; }
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stMain"], [data-testid="stMainBlockContainer"] {
 background: var(--wd-bg) !important; color: var(--wd-text) !important;
}
[data-testid="stHeader"] { background: transparent !important; }

[data-testid="stMainBlockContainer"] {
 max-width: 1500px !important; padding: 4.5rem clamp(1rem, 3.5vw, 3.5rem) 3.5rem !important;
}

[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li, [data-testid="stHeading"],
h1, h2, h3, h4, h5, h6 { color: var(--wd-text) !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--wd-muted) !important; }

.wd-brand { min-height: 52px; display:flex; align-items:center; gap:11px; }
.wd-logo { width:43px; height:43px; display:grid; place-items:center; border-radius:14px;
 background:var(--wd-primary); color:#fff; font-size:22px; font-weight:850;
 box-shadow:0 8px 24px var(--wd-glow); }
.wd-brand-name { color:var(--wd-text); font-size:23px; font-weight:850; letter-spacing:-.8px; line-height:1.1; }
.wd-brand-subtitle { color:var(--wd-muted); font-size:8px; font-weight:750; letter-spacing:1.4px; margin-top:4px; white-space:nowrap; }

div[data-testid="stRadio"] > label { display:none !important; }
div[data-testid="stRadio"] div[role="radiogroup"] { display:flex; flex-wrap:wrap; justify-content:center; gap:5px; }
div[data-testid="stRadio"] div[role="radiogroup"] label {
 background:transparent; border:1px solid transparent; border-radius:10px; padding:7px 10px;
 color:var(--wd-muted) !important; transition:all .15s ease; margin:0 !important; cursor:pointer;
}
div[data-testid="stRadio"] div[role="radiogroup"] label p { color:inherit !important; font-size:12px; font-weight:650; }
div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
 background:var(--wd-soft); border-color:var(--wd-border); color:var(--wd-text) !important;
}

div[data-testid="stRadio"] [data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display:none !important; }

[data-testid="stToggle"] label, [data-testid="stToggle"] p,
[data-testid="stCheckbox"] label, [data-testid="stCheckbox"] p {
 color:var(--wd-text) !important; font-size:12px !important; font-weight:650 !important;
}

.wd-rule { height:1px; background:var(--wd-border); margin:22px 0 28px; }
.wd-eyebrow, .wd-kicker { color:var(--wd-accent); font-size:10px; font-weight:850; letter-spacing:1.8px; }
.wd-eyebrow { display:inline-block; padding:9px 14px; border:1px solid var(--wd-border); border-radius:30px; background:var(--wd-soft); margin-bottom:22px; }
.wd-hero { padding:36px 8px 30px 0; }
.wd-hero h1 { max-width:680px; margin:0 0 20px; color:var(--wd-text); font-size:clamp(42px,5.2vw,70px); font-weight:850; line-height:1.06; letter-spacing:-3px; }
.wd-hero h1 span, .wd-title span { color:var(--wd-accent); }
.wd-copy { color:var(--wd-muted); font-size:15px; line-height:1.85; max-width:550px; }
.wd-pills { display:flex; flex-wrap:wrap; gap:8px; margin-top:22px; }
.wd-pills span { padding:8px 12px; border:1px solid var(--wd-border); border-radius:30px; background:var(--wd-soft); color:var(--wd-text); font-size:10px; font-weight:700; }
.wd-note { color:var(--wd-muted); font-size:11px; margin-top:25px; }
[data-testid="stVerticalBlockBorderWrapper"] { background:var(--wd-surface) !important; border:1px solid var(--wd-border) !important; border-radius:20px !important; box-shadow:0 12px 38px var(--wd-glow); }
.wd-panel-label { color:var(--wd-muted); font-size:9px; font-weight:800; letter-spacing:1.4px; }
.wd-panel-title { color:var(--wd-text); font-size:23px; font-weight:820; letter-spacing:-.7px; margin-top:6px; }
.wd-visual { margin:16px 0; padding:17px; border-radius:16px; color:#fff; background:radial-gradient(circle at 85% 12%,var(--wd-glow),transparent 38%),linear-gradient(135deg,var(--wd-visual1),var(--wd-visual2)); }
.wd-visual-top { display:flex; justify-content:space-between; color:rgba(255,255,255,.75); font-size:9px; font-weight:750; letter-spacing:1.1px; }
.wd-visual-main { display:flex; align-items:center; gap:15px; padding:22px 0; }
.wd-orbit { width:70px; height:70px; flex:0 0 70px; display:grid; place-items:center; border:1px solid rgba(255,255,255,.4); border-radius:50%; box-shadow:0 0 0 8px rgba(255,255,255,.05); }
.wd-orbit b { display:grid; place-items:center; width:48px; height:48px; border-radius:50%; background:var(--wd-accent); color:var(--wd-button-text); font-size:21px; }
.wd-visual strong { color:#fff; font-size:14px; }
.wd-visual p { color:rgba(255,255,255,.76); font-size:10px; line-height:1.6; margin:5px 0 0; }
.wd-visual-row { display:flex; justify-content:space-between; border-top:1px solid rgba(255,255,255,.17); padding:9px 0; color:#fff; font-size:10px; }
.wd-visual-row span:last-child { opacity:.75; }
.wd-title { color:var(--wd-text); font-size:clamp(26px,3vw,38px); line-height:1.2; font-weight:850; letter-spacing:-1.3px; margin:10px 0; }
.wd-subtitle { color:var(--wd-muted); font-size:13px; line-height:1.75; max-width:680px; }
.wd-card-label { color:var(--wd-accent); font-size:10px; font-weight:850; letter-spacing:1.2px; }
.wd-card-title { color:var(--wd-text); font-size:17px; font-weight:800; margin:16px 0 8px; }
.wd-card-copy { color:var(--wd-muted); font-size:12px; line-height:1.8; }
.wd-number { color:var(--wd-accent); font-size:25px; font-weight:850; }
.wd-footer { display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; color:var(--wd-muted); font-size:11px; padding:12px 0; }
.wd-footer strong { color:var(--wd-text); }

.stButton button p, [data-testid="stFormSubmitButton"] button p, [data-testid="stDownloadButton"] button p,
.stButton button [data-testid="stMarkdownContainer"] p, [data-testid="stFormSubmitButton"] button [data-testid="stMarkdownContainer"] p {
 color:var(--wd-button-text) !important;
}

[data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
 background:var(--wd-input) !important; color:var(--wd-text) !important; border-color:var(--wd-border) !important; border-radius:10px !important;
}
[data-testid="stTextInput"] label, [data-testid="stSelectbox"] label, [data-testid="stWidgetLabel"] p { color:var(--wd-text) !important; }
.stButton button, [data-testid="stFormSubmitButton"] button, [data-testid="stDownloadButton"] button {
 background:var(--wd-button) !important; color:var(--wd-button-text) !important; border:0 !important; border-radius:10px !important; font-weight:800 !important; min-height:42px;
}
[data-testid="stMetric"] { background:var(--wd-surface); border:1px solid var(--wd-border); border-radius:15px; padding:14px; }
[data-testid="stMetricLabel"] p { color:var(--wd-muted) !important; }
[data-testid="stMetricValue"] { color:var(--wd-text) !important; }
[data-testid="stDataFrame"] { border:1px solid var(--wd-border); border-radius:12px; }
[data-testid="stAlert"] { border-radius:12px; }
@media(max-width:900px) { .wd-hero h1 { font-size:46px; letter-spacing:-2px; } }
@media(max-width:600px) { .wd-hero h1 { font-size:38px; letter-spacing:-1px; } .wd-footer { flex-direction:column; } }
</style>
"""

repls = {
    "__BG__": C["bg"], "__SURFACE__": C["surface"], "__SURFACE2__": C["surface2"],
    "__PRIMARY__": C["primary"], "__ACCENT__": C["accent"], "__TEXT__": C["text"],
    "__MUTED__": C["muted"], "__SOFT__": C["soft"], "__BORDER__": C["border"],
    "__INPUT__": C["input"], "__BUTTON_TEXT__": C["button_text"], "__BUTTON__": C["button"],
    "__VISUAL1__": C["visual1"], "__VISUAL2__": C["visual2"], "__GLOW__": C["glow"],
    "__SUCCESS__": C["success"], "__WARNING__": C["warning"], "__DANGER__": C["danger"],
}
for old, new in repls.items():
    CSS = CSS.replace(old, new)
st.html(CSS)


def page_heading(kicker: str, title: str, subtitle: str):
    st.html(
        f'<div class="wd-kicker">{kicker}</div>'
        f'<div class="wd-title">{title}</div>'
        f'<div class="wd-subtitle">{subtitle}</div>'
    )


def info_card(number: str, title: str, copy: str, tag: str = ""):
    with st.container(border=True):
        st.html(
            f'<div class="wd-card-label">{number} {tag}</div>'
            f'<div class="wd-card-title">{title}</div>'
            f'<div class="wd-card-copy">{copy}</div>'
        )


def load_latest_scan_data():
    """Load the newest persisted scan so all result pages stay in sync."""
    if SCANNER_RESULTS_FILE.exists():
        try:
            with SCANNER_RESULTS_FILE.open("r", encoding="utf-8") as file:
                latest_scan = json.load(file)
            if isinstance(latest_scan, dict):
                st.session_state.wd_scan_data = latest_scan
                return latest_scan
        except (json.JSONDecodeError, OSError) as exc:
            st.warning(f"Could not read the latest scanner results: {exc}")

    # Use cached session data only when no valid persisted scan is available.
    cached_scan = st.session_state.get("wd_scan_data")
    return cached_scan if isinstance(cached_scan, dict) else None


if selected_page == "Home":
    left, right = st.columns([1.08, 0.92], gap="large", vertical_alignment="center")
    with left:
        st.html(
            """
            <section class="wd-hero">
              <div class="wd-eyebrow">INTELLIGENT WEB ACCESSIBILITY</div>
              <h1>The web should<br>work for <span>everyone.</span></h1>
              <p class="wd-copy">Your website deserves more than a basic accessibility score. Discover barriers, understand who they affect, and create a better digital experience with AI-powered guidance.</p>
              <div class="wd-pills"><span>WCAG analysis</span><span>AI remediation</span><span>Inclusive design</span></div>
              <div class="wd-note">A smarter way to build an inclusive web.</div>
            </section>
            """
        )
    with right:
        with st.container(border=True):
            st.html(
                """
                <div class="wd-panel-label">YOUR ACCESSIBILITY WORKSPACE</div>
                <div class="wd-panel-title">Start with a scan.</div>
                <div class="wd-visual">
                  <div class="wd-visual-top"><span>WEBSITE DIAGNOSTICS</span><span>WEBDOC / 01</span></div>
                  <div class="wd-visual-main"><div class="wd-orbit"><b>W</b></div><div><strong>Every detail matters.</strong><p>Understand your website from every user's perspective.</p></div></div>
                  <div class="wd-visual-row"><span>01 / Page structure</span><span>Ready to check</span></div>
                  <div class="wd-visual-row"><span>02 / Visual accessibility</span><span>Ready to check</span></div>
                  <div class="wd-visual-row"><span>03 / Keyboard access</span><span>Ready to check</span></div>
                </div>
                <div class="wd-card-title">Enter your website URL</div>
                <div class="wd-card-copy">We'll analyse the page and identify accessibility barriers.</div>
                """
            )
            with st.form("website_scan_form", clear_on_submit=False):
                url_input = st.text_input("Website URL", value=st.session_state.wd_url, placeholder="https://yourwebsite.com", label_visibility="collapsed")
                scan_submit = st.form_submit_button("Analyse website", width="stretch")
            if scan_submit:
                candidate = normalise_url(url_input)

                if candidate is None:
                    st.error("Please enter a valid website URL.")
                else:
                    st.session_state.wd_url = candidate

                    with st.spinner(
                        "Scanning website and generating AI accessibility analysis..."
                    ):
                        try:
                            result = run_full_scan(candidate)

                            st.session_state.wd_scan_data = result["scan"]
                            st.session_state.wd_ai_data = result["ai"]
                            st.session_state.wd_scan_log = result.get("scanner_log", "")
                            st.session_state.wd_ai_log = result.get("ai_log", "")
                            st.session_state.wd_scan_error = None

                            st.session_state.wd_goto = "Dashboard"
                            st.rerun()

                        except Exception as exc:
                            st.session_state.wd_scan_error = str(exc)
                            st.error(f"Website analysis failed: {exc}")

    st.html('<div class="wd-rule"></div>')
    metrics = st.columns(3)
    for col, value, label in zip(metrics, ["06", "WCAG", "AI"], ["ACCESSIBILITY PERSPECTIVES", "GUIDED ANALYSIS", "INTELLIGENT REMEDIATION"]):
        with col:
            st.html(f'<div class="wd-number">{value}</div><div class="wd-card-copy">{label}</div>')
    st.html('<div class="wd-rule"></div>')
    page_heading("WHAT WE DO", "From accessibility barriers <span>to better experiences.</span>", "Understand, improve and verify website accessibility in one workspace.")
    feature_cols = st.columns(3, gap="medium")
    for col, data in zip(feature_cols, [
        ("01", "Intelligent diagnosis", "Detect accessibility violations and understand how they affect real users.", "DETECT"),
        ("02", "AI-powered remediation", "Get clear explanations and practical HTML/CSS fixes for accessibility problems.", "IMPROVE"),
        ("03", "Verified improvements", "Compare original and corrected pages and verify improvements with a fresh scan.", "VERIFY"),
    ]):
        with col:
            info_card(data[0], data[1], data[2], data[3])
    st.html('<div class="wd-rule"></div>')
    page_heading("THE WEBDOC PROCESS", "Three steps towards <span>an inclusive web.</span>", "Diagnose the issue, understand its impact, then verify the fix.")
    step_cols = st.columns(3)
    for col, data in zip(step_cols, [("01", "Diagnose", "Scan a website and discover accessibility barriers."), ("02", "Understand", "See who is affected and prioritise the problems."), ("03", "Transform", "Generate fixes and verify improvements.")]):
        with col:
            info_card(data[0], data[1], data[2])


elif selected_page == "Dashboard":
    page_heading(
        "OVERVIEW",
        "Accessibility <span>dashboard.</span>",
        "A live summary of the latest accessibility scan for your website."
    )

    # Always prefer the latest saved result, not an older Streamlit session cache.
    scan_data = load_latest_scan_data()

    if not isinstance(scan_data, dict):
        st.info(
            "No scan results are available yet. Go to Home and analyse a website first."
        )
    else:
        summary = scan_data.get("summary")
        if not isinstance(summary, dict):
            summary = {}

        violations = scan_data.get("violations")
        if not isinstance(violations, list):
            violations = []

        website_url = (
            scan_data.get("final_url")
            or scan_data.get("url")
            or st.session_state.get("wd_url")
            or "Website URL not recorded"
        )
        st.caption(f"Website analysed: {website_url}")

        scan_timestamp = scan_data.get("timestamp")
        if scan_timestamp:
            st.caption(f"Latest scan: {scan_timestamp}")

        def dashboard_count(value, fallback=0):
            try:
                return max(0, int(value))
            except (TypeError, ValueError):
                return fallback

        total_violations = dashboard_count(
            summary.get("total_violations"),
            len(violations)
        )

        calculated_affected_nodes = sum(
            dashboard_count(
                item.get("affected_nodes"),
                len(item.get("nodes") or [])
            )
            for item in violations
            if isinstance(item, dict)
        )
        total_affected_nodes = dashboard_count(
            summary.get("total_affected_nodes"),
            calculated_affected_nodes
        )

        impact_counts = summary.get("impact_counts")
        if not isinstance(impact_counts, dict):
            impact_counts = {}

        severity_labels = ["Critical", "Serious", "Moderate", "Minor"]
        severity_values = []

        for severity in severity_labels:
            severity_key = severity.lower()
            fallback_count = sum(
                1
                for item in violations
                if isinstance(item, dict)
                and str(item.get("impact") or "").lower() == severity_key
            )
            severity_values.append(
                dashboard_count(
                    impact_counts.get(severity_key),
                    fallback_count
                )
            )

        passes_value = summary.get("passes")
        incomplete_value = summary.get("incomplete")
        passes_display = (
            dashboard_count(passes_value)
            if passes_value is not None
            else "—"
        )
        incomplete_display = (
            dashboard_count(incomplete_value)
            if incomplete_value is not None
            else "—"
        )

        # Main metrics are taken directly from the scanner output.
        st.subheader("Scan overview")
        metric_cols = st.columns(4)
        metric_cols[0].metric("Total violations", total_violations)
        metric_cols[1].metric("Affected nodes", total_affected_nodes)
        metric_cols[2].metric("Passed checks", passes_display)
        metric_cols[3].metric("Incomplete checks", incomplete_display)

        if scan_data.get("score") is None:
            st.caption(
                "Accessibility score: not calculated by this scan. "
                "WebDoc does not substitute a demo or estimated score."
            )
        else:
            st.caption(f"Scanner score: {scan_data.get('score')}")

        st.divider()

        # Severity breakdown.
        st.subheader("Issue severity")
        severity_cols = st.columns(4)
        for col, label, value in zip(
            severity_cols,
            severity_labels,
            severity_values
        ):
            with col:
                st.metric(label, value)

        st.subheader("Issue distribution")
        severity_chart_data = {
            "Severity": severity_labels,
            "Violations": severity_values
        }
        st.bar_chart(
            severity_chart_data,
            x="Severity",
            y="Violations",
            x_label="Severity",
            y_label="Number of violations"
        )

        st.divider()

        # Show the actual rules returned by axe-core.
        st.subheader("Detected accessibility issues")
        issue_rows = []

        for item in violations:
            if not isinstance(item, dict):
                continue

            nodes = item.get("nodes")
            if not isinstance(nodes, list):
                nodes = []

            affected_count = dashboard_count(
                item.get("affected_nodes"),
                len(nodes)
            )

            issue_rows.append({
                "Issue": item.get("help") or item.get("id") or "Unknown issue",
                "Rule ID": item.get("id") or "N/A",
                "Severity": str(item.get("impact") or "Unknown").title(),
                "Affected nodes": affected_count
            })

        if issue_rows:
            st.dataframe(
                issue_rows,
                width="stretch",
                hide_index=True
            )
        else:
            st.info("The scanner did not return any accessibility violations.")

        st.divider()
        st.subheader("Recommended next steps")

        critical_count = severity_values[0]
        serious_count = severity_values[1]

        if critical_count or serious_count:
            st.write(
                f"1. Review the {critical_count} critical and "
                f"{serious_count} serious issue(s) first."
            )
        else:
            st.write("1. Review the detected moderate and minor issues.")

        st.write("2. Open WCAG Issues to inspect each rule and affected element.")
        st.write("3. Review AI Co-Pilot suggestions, then make changes manually.")
        st.write("4. Run a fresh scan to verify any changes.")
elif selected_page == "WCAG Issues":
    page_heading(
        "DIAGNOSIS",
        "WCAG <span>issues.</span>",
        "Review actual accessibility violations detected on your website."
    )

    # Always prefer the latest saved result, not an older Streamlit session cache.
    scan_data = load_latest_scan_data()

    if not isinstance(scan_data, dict):
        st.info(
            "No scan results are available yet. Go to Home and analyse a website first."
        )
    else:
        summary = scan_data.get("summary")
        if not isinstance(summary, dict):
            summary = {}

        violations = scan_data.get("violations")
        if not isinstance(violations, list):
            violations = []

        website_url = (
            scan_data.get("final_url")
            or scan_data.get("url")
            or st.session_state.get("wd_url")
            or "Website URL not recorded"
        )
        st.caption(f"Website analysed: {website_url}")

        scan_timestamp = scan_data.get("timestamp")
        if scan_timestamp:
            st.caption(f"Latest scan: {scan_timestamp}")

        def wcag_count(value, fallback=0):
            try:
                return max(0, int(value))
            except (TypeError, ValueError):
                return fallback

        impact_counts = summary.get("impact_counts")
        if not isinstance(impact_counts, dict):
            impact_counts = {}

        severity_options = ["Critical", "Serious", "Moderate", "Minor"]
        severity_counts = {}

        for severity in severity_options:
            key = severity.lower()
            fallback_count = sum(
                1
                for item in violations
                if isinstance(item, dict)
                and str(item.get("impact") or "").lower() == key
            )
            severity_counts[severity] = wcag_count(
                impact_counts.get(key),
                fallback_count
            )

        metric_cols = st.columns(4)
        for col, severity in zip(metric_cols, severity_options):
            with col:
                col.metric(severity, severity_counts[severity])

        st.divider()

        if not violations:
            st.success(
                "The scanner did not return any accessibility violations for this page."
            )
        else:
            filter_col, search_col = st.columns([1, 2])

            with filter_col:
                selected_severity = st.selectbox(
                    "Filter by severity",
                    ["All"] + severity_options,
                    key="wcag_severity_filter"
                )

            with search_col:
                search_text = st.text_input(
                    "Search issues",
                    placeholder="Search issue name or rule ID",
                    key="wcag_issue_search"
                ).strip().lower()

            filtered_violations = []

            for issue in violations:
                if not isinstance(issue, dict):
                    continue

                issue_severity = str(
                    issue.get("impact") or "Unknown"
                ).title()

                if (
                    selected_severity != "All"
                    and issue_severity != selected_severity
                ):
                    continue

                issue_id = str(issue.get("id") or "")
                issue_title = str(issue.get("help") or issue_id)
                searchable_text = f"{issue_title} {issue_id}".lower()

                if search_text and search_text not in searchable_text:
                    continue

                filtered_violations.append(issue)

            st.caption(
                f"Showing {len(filtered_violations)} of "
                f"{len(violations)} detected violations."
            )

            if not filtered_violations:
                st.info("No issues match the selected filter.")
            else:
                for issue in filtered_violations:
                    issue_id = issue.get("id") or "unknown-rule"
                    issue_title = issue.get("help") or issue_id
                    severity = str(
                        issue.get("impact") or "Unknown"
                    ).title()
                    description = issue.get("description") or (
                        "No description was supplied by the scanner."
                    )

                    nodes = issue.get("nodes")
                    if not isinstance(nodes, list):
                        nodes = []

                    affected_count = wcag_count(
                        issue.get("affected_nodes"),
                        len(nodes)
                    )

                    with st.container(border=True):
                        title_col, severity_col = st.columns([3, 1])

                        with title_col:
                            st.markdown(f"### {issue_title}")
                            st.caption(f"Rule ID: `{issue_id}`")

                        with severity_col:
                            st.metric("Severity", severity)

                        st.write(description)
                        st.write(f"**Affected elements:** {affected_count}")

                        # Display WCAG tags only when the scanner actually supplies them.
                        wcag_tags = issue.get("tags")
                        if isinstance(wcag_tags, str):
                            wcag_tags = [wcag_tags]
                        elif not isinstance(wcag_tags, list):
                            wcag_tags = []

                        if wcag_tags:
                            st.caption(
                                "Scanner tags: "
                                + ", ".join(str(tag) for tag in wcag_tags)
                            )
                        else:
                            st.caption(
                                "WCAG success criterion was not included "
                                "in this scanner result; no criterion has been inferred."
                            )

                        help_url = issue.get("help_url")
                        if help_url:
                            st.markdown(
                                f"[Open rule guidance]({help_url})"
                            )

                        if nodes:
                            with st.expander(
                                f"Inspect affected elements ({len(nodes)})"
                            ):
                                for index, node in enumerate(nodes, start=1):
                                    if not isinstance(node, dict):
                                        continue

                                    st.markdown(f"**Affected element {index}**")

                                    targets = node.get("target") or []
                                    if isinstance(targets, str):
                                        targets = [targets]

                                    if targets:
                                        st.caption(
                                            "CSS target: "
                                            + ", ".join(str(target) for target in targets)
                                        )

                                    html_fragment = node.get("html")
                                    if html_fragment:
                                        st.code(
                                            str(html_fragment)[:3000],
                                            language="html"
                                        )

                                    failure_summary = node.get("failure_summary")
                                    if failure_summary:
                                        st.markdown("**Scanner failure details**")
                                        st.text(str(failure_summary)[:3000])


elif selected_page == "Profiles":
    page_heading("USER IMPACT", "Accessibility <span>profiles.</span>", "Understand how barriers can affect people with different access needs.")
    profile_data = [
        ("Blind users", "Screen-reader labels, landmarks and semantic structure.", 65),
        ("Low-vision users", "Contrast, text resizing and magnification.", 72),
        ("Colour-blind users", "Colour-independent cues and visual distinctions.", 78),
        ("Deaf and hard-of-hearing users", "Captions and alternatives to audio.", 86),
        ("Keyboard-only users", "Focus visibility and keyboard operability.", 60),
        ("Cognitive and reading needs", "Clear structure, language and predictable interactions.", 81),
    ]
    cols = st.columns(3, gap="medium")
    for col, (name, desc, score) in zip(cols * 2, profile_data):
        with col:
            with st.container(border=True):
                st.markdown(f"**{name}**")
                st.progress(score / 100)
                st.caption(f"Illustrative profile score: {score}/100")
                st.write(desc)


elif selected_page == "Heatmap":
    page_heading("VISUAL DIAGNOSIS", "Accessibility <span>heatmap.</span>", "Locate detected issues visually and inspect the affected page elements.")
    st.info("The visual overlay will become interactive when Person 1's scanner supplies a screenshot and element selectors. This screen currently shows the integration placeholder.")
    with st.container(border=True):
        st.markdown("**Detected element markers — sample data**")
        for label, selector, severity in [("Missing image alternative text", "img.hero-image", "Critical"), ("Button accessible name", "button.checkout", "Serious"), ("Low text contrast", "p.description", "Moderate")]:
            st.write(f"{severity}  ·  `{selector}`  ·  {label}")


elif selected_page == "AI Co-Pilot":
    page_heading(
        "AI REMEDIATION",
        "Your accessibility <span>co-pilot.</span>",
        "Review Gemini explanations, suggested fixes and patch validation for detected accessibility issues.",
    )

    if not AI_RESULTS_FILE.exists():
        st.error("AI results file was not found.")
        st.caption(f"Expected file: {AI_RESULTS_FILE}")
    else:
        try:
            with AI_RESULTS_FILE.open("r", encoding="utf-8") as results_file:
                ai_data = json.load(results_file)
        except json.JSONDecodeError as exc:
            st.error("The AI results file contains invalid JSON.")
            st.caption(f"JSON detail: {exc}")
            ai_data = None
        except OSError as exc:
            st.error("Could not read the AI results file.")
            st.caption(str(exc))
            ai_data = None

        if ai_data is not None:
            results = ai_data.get("results", [])
            if not isinstance(results, list):
                results = []

            successful_results = [
                item for item in results
                if isinstance(item, dict)
                and isinstance(item.get("analysis"), dict)
                and item.get("status") != "failed"
            ]
            failed_results = [
                item for item in results
                if isinstance(item, dict)
                and (item.get("status") == "failed" or item.get("error"))
            ]

            total_violations = ai_data.get("total_violations", len(results))
            successful_count = ai_data.get("successful_analyses", len(successful_results))
            failed_count = ai_data.get("failed_analyses", len(failed_results))

            st.caption(f"Website: {ai_data.get('source_url') or 'URL not included in results'}")
            metric_cols = st.columns(3)
            metric_cols[0].metric("Total violations", total_violations)
            metric_cols[1].metric("Successful analyses", successful_count)
            metric_cols[2].metric("Failed analyses", failed_count)

            if successful_results:
                def result_label(item):
                    analysis = item.get("analysis", {})
                    issue_id = item.get("issue_id") or "Accessibility issue"
                    problem = analysis.get("problem") or "AI explanation available"
                    return f"{issue_id} — {problem}"

                selected_index = st.selectbox(
                    "Choose an analysed issue",
                    range(len(successful_results)),
                    format_func=lambda index: result_label(successful_results[index]),
                    key="ai_copilot_issue_index",
                )
                selected_result = successful_results[selected_index]
                analysis = selected_result.get("analysis", {})
                patch_data = selected_result.get("patch") or {}

                st.markdown(
                    f"### {analysis.get('problem') or selected_result.get('issue_id', 'Accessibility issue')}"
                )
                with st.container(border=True):
                    st.markdown("**What is the problem?**")
                    st.write(analysis.get("explanation") or "No explanation was included in the AI result.")

                    affected_users = analysis.get("affected_users")
                    if affected_users:
                        st.markdown("**Who may be affected?**")

                        # Gemini output may encode this field as a list or as
                        # an indexed object such as {"0": "...", "1": "..."}.
                        if isinstance(affected_users, dict):
                            affected_user_items = [
                                affected_users[key]
                                for key in sorted(
                                    affected_users,
                                    key=lambda item: str(item)
                                )
                            ]
                        elif isinstance(affected_users, (list, tuple)):
                            affected_user_items = list(affected_users)
                        elif isinstance(affected_users, str):
                            affected_user_items = [affected_users]
                        else:
                            affected_user_items = [str(affected_users)]

                        for affected_user in affected_user_items:
                            if isinstance(affected_user, str):
                                st.markdown(f"- {affected_user}")
                            else:
                                st.markdown(f"- {affected_user}")

                    wcag_reference = analysis.get("wcag_reference")
                    st.markdown("**WCAG reference**")
                    st.write(
                        wcag_reference
                        if wcag_reference
                        else "Not supplied by the scanner; no criterion inferred."
                    )

                    recommended_fix = analysis.get("recommended_fix")
                    if recommended_fix:
                        st.markdown("**Recommended fix**")
                        st.write(recommended_fix)

                    original_code = patch_data.get("original_code")
                    corrected_code = (
                        patch_data.get("corrected_code")
                        or analysis.get("corrected_code")
                    )
                    code_language = analysis.get("code_language") or "html"

                    if original_code:
                        st.markdown("**Original code**")
                        st.code(original_code, language=code_language)
                    if corrected_code:
                        st.markdown("**Suggested correction**")
                        st.code(corrected_code, language=code_language)
                    elif not recommended_fix:
                        st.info("No code correction was returned for this issue.")

                validation = patch_data.get("validation") or {}
                patch_applicable = patch_data.get("patch_applicable")
                verification_status = patch_data.get("verification_status")
                review_required = (
                    patch_data.get("human_review_required")
                    if patch_data.get("human_review_required") is not None
                    else analysis.get("human_review_required")
                )

                with st.container(border=True):
                    st.markdown("**Patch validation and review**")
                    if validation.get("valid") is True:
                        st.success("Patch passed the available code validation checks.")
                    elif validation.get("valid") is False:
                        st.warning("Patch did not pass the available code validation checks.")
                    else:
                        st.info("No patch validation result was provided.")

                    if patch_applicable is True:
                        st.write("Patch applicability: marked applicable by the remediation validator.")
                    elif patch_applicable is False:
                        st.warning(
                            "Patch is not marked safe to apply automatically. Review the page context first."
                        )
                    if verification_status:
                        st.write(f"Verification status: {verification_status}")
                    if review_required:
                        st.warning("Human review is required. Re-scan the page after any manual change.")

                    review_note = patch_data.get("review_note")
                    if review_note:
                        st.write(review_note)

                    validation_problems = validation.get("problems") or []
                    validation_warnings = validation.get("warnings") or []
                    if validation_problems:
                        st.markdown("**Validation problems**")
                        for problem in validation_problems:
                            st.write(f"- {problem}")
                    if validation_warnings:
                        st.markdown("**Validation warnings**")
                        for warning in validation_warnings:
                            st.write(f"- {warning}")

                verification_steps = analysis.get("verification_steps") or []
                if verification_steps:
                    with st.expander("Verification steps"):
                        for step in verification_steps:
                            st.write(f"- {step}")
            else:
                st.info("No successful Gemini analyses are present in this results file yet.")

            if failed_results:
                with st.expander(f"Failed analyses ({len(failed_results)})"):
                    for failed_item in failed_results:
                        st.markdown(f"**{failed_item.get('issue_id', 'Unknown issue')}**")
                        st.write(
                            failed_item.get("error")
                            or "Analysis failed without an error message."
                        )

            st.caption(
                "These suggestions are AI-generated. Review changes and run a fresh accessibility scan before deploying them."
            )


elif selected_page == "Preview":
    page_heading("REMEDIATION", "Before & <span>after.</span>", "Compare the original page with a temporary corrected preview.")
    before, after = st.columns(2)
    with before:
        with st.container(border=True):
            st.markdown("**Original example**")
            st.code('<button></button>', language="html")
            st.error("Accessible name missing")
    with after:
        with st.container(border=True):
            st.markdown("**Corrected example**")
            st.code('<button aria-label="Submit">Submit</button>', language="html")
            st.success("Accessible name added — still requires re-scan verification")
    st.caption("The preview will use Person 2's patch output and a sandboxed rendering step.")


elif selected_page == "Journey":
    page_heading("INTERACTION TESTING", "Accessibility <span>journey.</span>", "Check whether a keyboard-only user can complete a key task on a website.")
    journey = [("1", "Open homepage", "Passed"), ("2", "Move to product search", "Passed"), ("3", "Open product details", "Passed"), ("4", "Add item to cart", "Needs testing"), ("5", "Continue to checkout", "Not reached")]
    for number, label, result in journey:
        with st.container(border=True):
            a, b = st.columns([3, 1])
            with a:
                st.markdown(f"**Step {number}: {label}**")
            with b:
                st.caption(result)
    st.caption("Sample journey only. Person 1's keyboard and journey test module will provide real results.")


st.divider()
st.markdown("<div class='wd-footer'><strong>WebDoc · AI Website Accessibility Doctor</strong><span>Building a more inclusive digital world.</span></div>", unsafe_allow_html=True)