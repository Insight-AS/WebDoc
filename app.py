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



def read_optional_json(path):
    """Read an optional JSON report without interrupting the dashboard."""
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as file:
            value = json.load(file)
        return value if isinstance(value, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _report_plain(value, limit=1800):
    """Convert arbitrary JSON values to readable, bounded report text."""
    if value is None:
        return "Not supplied"
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, ensure_ascii=False, indent=2)
    text_value = str(value).strip()
    if not text_value:
        return "Not supplied"
    if len(text_value) > limit:
        text_value = text_value[:limit].rstrip() + " … [truncated]"
    return text_value


def build_full_report_pdf(scan_data, ai_data, journey_data, keyboard_data):
    """Build a downloadable PDF from the latest saved WebDoc audit outputs."""
    from io import BytesIO
    from xml.sax.saxutils import escape
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak,
        KeepTogether, Image as ReportImage,
    )

    scan_data = scan_data if isinstance(scan_data, dict) else {}
    ai_data = ai_data if isinstance(ai_data, dict) else {}
    journey_data = journey_data if isinstance(journey_data, dict) else {}
    keyboard_data = keyboard_data if isinstance(keyboard_data, dict) else {}

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=17 * mm,
        leftMargin=17 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
        title="WebDoc Accessibility Audit Report",
        author="WebDoc - AI Website Accessibility Doctor",
    )

    navy = colors.HexColor("#173F60")
    coral = colors.HexColor("#E7776D")
    pale = colors.HexColor("#EEF4F8")
    muted = colors.HexColor("#5F7182")
    green = colors.HexColor("#217A58")
    orange = colors.HexColor("#B66A18")
    red = colors.HexColor("#B83D48")

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=25, leading=30, textColor=navy, alignment=TA_LEFT,
        spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="ReportSubtitle", parent=styles["Normal"], fontSize=10,
        leading=15, textColor=muted, spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="SectionHeading", parent=styles["Heading2"], fontName="Helvetica-Bold",
        fontSize=14, leading=18, textColor=navy, spaceBefore=12, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="SmallBody", parent=styles["BodyText"], fontSize=8.5,
        leading=12, textColor=colors.HexColor("#263746"), spaceAfter=4,
    ))
    styles.add(ParagraphStyle(
        name="TinyBody", parent=styles["BodyText"], fontSize=7.3,
        leading=9.5, textColor=muted,
    ))
    styles.add(ParagraphStyle(
        name="CodeBody", parent=styles["Code"], fontName="Courier",
        fontSize=6.6, leading=8.2, textColor=colors.HexColor("#293848"),
        backColor=pale, borderPadding=5, spaceBefore=3, spaceAfter=7,
    ))
    styles.add(ParagraphStyle(
        name="WhiteLabel", parent=styles["Normal"], fontSize=8,
        leading=10, textColor=colors.white,
    ))

    def para(value, style="SmallBody", limit=1800):
        raw = _report_plain(value, limit=limit)
        safe = escape(raw).replace("\n", "<br/>")
        return Paragraph(safe, styles[style])

    def make_table(rows, widths=None, header=True):
        converted = []
        for row_index, row in enumerate(rows):
            converted.append([
                cell if isinstance(cell, (Paragraph,)) else para(cell, "TinyBody", 500)
                for cell in row
            ])
        table = Table(converted, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
        commands = [
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D8E2EA")),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]
        if header:
            commands.extend([
                ("BACKGROUND", (0, 0), (-1, 0), navy),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ])
            # Use explicit white header paragraphs for reliable contrast.
            for col_index, cell in enumerate(rows[0]):
                converted[0][col_index] = Paragraph(escape(str(cell)), styles["WhiteLabel"])
            table = Table(converted, colWidths=widths, repeatRows=1, hAlign="LEFT")
        else:
            commands.append(("BACKGROUND", (0, 0), (-1, -1), pale))
        table.setStyle(TableStyle(commands))
        return table

    violations = scan_data.get("violations", [])
    if not isinstance(violations, list):
        violations = []
    summary = scan_data.get("summary", {})
    if not isinstance(summary, dict):
        summary = {}
    impacts = summary.get("impact_counts", {})
    if not isinstance(impacts, dict):
        impacts = {}

    ai_results = ai_data.get("results", [])
    if not isinstance(ai_results, list):
        ai_results = []
    ai_lookup = {
        str(item.get("issue_id")): item
        for item in ai_results
        if isinstance(item, dict) and item.get("issue_id")
    }
    successful_ai = sum(
        1 for item in ai_results
        if isinstance(item, dict) and isinstance(item.get("analysis"), dict)
        and item.get("status") != "failed"
    )
    failed_ai = sum(
        1 for item in ai_results
        if isinstance(item, dict) and (item.get("status") == "failed" or item.get("error"))
    )

    journey_results = journey_data.get("results", [])
    if not isinstance(journey_results, list):
        journey_results = []
    links = [item for item in journey_results if isinstance(item, dict) and item.get("step") == "Check navigation link"]
    focus_items = keyboard_data.get("focused_elements", [])
    if not isinstance(focus_items, list):
        focus_items = []

    website = (
        scan_data.get("final_url") or scan_data.get("url")
        or journey_data.get("url") or keyboard_data.get("url") or "Not recorded"
    )
    generated_at = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    story = []
    story.append(Paragraph("WEBDOC", ParagraphStyle(
        "Brand", parent=styles["Normal"], fontName="Helvetica-Bold",
        fontSize=10, textColor=coral, leading=13, spaceAfter=8,
    )))
    story.append(Paragraph("Accessibility Audit Report", styles["ReportTitle"]))
    story.append(Paragraph(
        "Automated website accessibility findings, AI remediation guidance, "
        "visual scan data, and browser-based keyboard checks.",
        styles["ReportSubtitle"],
    ))
    story.append(para(f"Website: {website}", limit=1000))
    story.append(para(f"Report generated: {generated_at}"))
    story.append(para(f"Scan timestamp: {scan_data.get('timestamp', 'Not available')}"))
    story.append(Spacer(1, 8))

    total_violations = summary.get("total_violations", len(violations))
    affected_nodes = summary.get("total_affected_nodes", sum(
        len(item.get("nodes", [])) for item in violations if isinstance(item, dict)
    ))
    overview_rows = [
        ["Metric", "Result", "Metric", "Result"],
        ["Accessibility violations", total_violations, "Affected nodes", affected_nodes],
        ["Passed axe-core rules", summary.get("passes", "Not supplied"), "Incomplete rules", summary.get("incomplete", "Not supplied")],
        ["Gemini analyses succeeded", successful_ai, "Gemini analyses failed", failed_ai],
        ["Navigation links inspected", len(links), "Keyboard focus stops", len(focus_items)],
    ]
    story.append(Paragraph("Executive summary", styles["SectionHeading"]))
    story.append(make_table(overview_rows, [43*mm, 25*mm, 43*mm, 25*mm]))

    story.append(Paragraph("Severity breakdown", styles["SectionHeading"]))
    severity_rows = [["Critical", "Serious", "Moderate", "Minor"]]
    severity_rows.append([impacts.get("critical", 0), impacts.get("serious", 0), impacts.get("moderate", 0), impacts.get("minor", 0)])
    story.append(make_table(severity_rows, [34*mm, 34*mm, 34*mm, 34*mm]))

    # Include the actual viewport screenshot captured by the scanner, when available.
    screenshot_path = PROJECT_DIR / "data" / "website_screenshot.png"
    if screenshot_path.exists():
        try:
            from PIL import Image as PILImage
            with PILImage.open(screenshot_path) as screenshot_file:
                screenshot_width, screenshot_height = screenshot_file.size
            max_width = 174 * mm
            max_height = 205 * mm
            image_scale = min(
                max_width / max(1, screenshot_width),
                max_height / max(1, screenshot_height),
            )
            story.append(Paragraph("Scanned page screenshot", styles["SectionHeading"]))
            story.append(para(
                "Viewport capture saved by the Playwright scanner. The image is included as visual context; it is not a full-page capture.",
                limit=300,
            ))
            story.append(ReportImage(
                str(screenshot_path),
                width=screenshot_width * image_scale,
                height=screenshot_height * image_scale,
            ))
        except Exception:
            story.append(para("The scanner screenshot was present but could not be embedded in this PDF."))

    story.append(Paragraph("Accessibility findings and AI guidance", styles["SectionHeading"]))
    if not violations:
        story.append(para("No accessibility violations were recorded in the available scan file."))
    for index, issue in enumerate(violations, start=1):
        if not isinstance(issue, dict):
            continue
        issue_id = str(issue.get("id") or "unknown-rule")
        heading = f"{index}. {issue.get('help') or issue_id}  [{issue.get('impact') or 'severity not supplied'}]"
        issue_parts = [Paragraph(escape(heading), styles["Heading3"])]
        issue_parts.append(para(f"Rule ID: {issue_id} · Affected nodes: {issue.get('affected_nodes', len(issue.get('nodes') or []))}"))
        if issue.get("description"):
            issue_parts.append(para(issue.get("description"), limit=1000))
        ai_item = ai_lookup.get(issue_id, {})
        analysis = ai_item.get("analysis", {}) if isinstance(ai_item, dict) else {}
        if isinstance(analysis, dict) and analysis:
            issue_parts.append(para("Gemini explanation: " + str(analysis.get("explanation") or analysis.get("problem") or "Not supplied"), limit=1300))
            if analysis.get("affected_users"):
                issue_parts.append(para("Potentially affected users: " + _report_plain(analysis.get("affected_users"), 500), limit=600))
            if analysis.get("recommended_fix"):
                issue_parts.append(para("Recommended fix: " + str(analysis.get("recommended_fix")), limit=1100))
            if analysis.get("wcag_reference"):
                issue_parts.append(para("WCAG reference supplied by AI: " + str(analysis.get("wcag_reference")), limit=300))
            patch_data = ai_item.get("patch", {}) if isinstance(ai_item, dict) else {}
            if not isinstance(patch_data, dict):
                patch_data = {}
            original_patch = patch_data.get("original_code")
            corrected_patch = patch_data.get("corrected_code") or analysis.get("corrected_code")
            if original_patch:
                issue_parts.append(para("Original HTML fragment:", limit=100))
                issue_parts.append(Paragraph(
                    escape(_report_plain(original_patch, 650)).replace("\n", "<br/>"),
                    styles["CodeBody"],
                ))
            if corrected_patch:
                issue_parts.append(para("Gemini-suggested HTML correction:", limit=120))
                issue_parts.append(Paragraph(
                    escape(_report_plain(corrected_patch, 650)).replace("\n", "<br/>"),
                    styles["CodeBody"],
                ))
        nodes = issue.get("nodes", [])
        if isinstance(nodes, list) and nodes:
            first_node = nodes[0] if isinstance(nodes[0], dict) else {}
            if first_node.get("target"):
                issue_parts.append(para("Example target: " + _report_plain(first_node.get("target"), 400), limit=500))
            if first_node.get("failure_summary"):
                issue_parts.append(para("Scanner details: " + str(first_node.get("failure_summary")), limit=800))
        issue_parts.append(Spacer(1, 5))
        story.append(KeepTogether(issue_parts))

    story.append(Paragraph("Browser journey audit", styles["SectionHeading"]))
    if journey_data:
        story.append(para(f"Journey test URL: {journey_data.get('url', 'Not recorded')} · Timestamp: {journey_data.get('timestamp', 'Not recorded')}"))
        journey_rows = [["Test step", "Status", "Details"]]
        for item in journey_results:
            if not isinstance(item, dict):
                continue
            details = item.get("link_text") or item.get("title") or item.get("error") or ""
            if item.get("href"):
                details = f"{details} — {item.get('href')}"
            if item.get("total_buttons") is not None:
                details = f"Buttons: {item.get('total_buttons')}"
            if item.get("total_forms") is not None:
                details = f"Forms: {item.get('total_forms')}"
            journey_rows.append([item.get("step", "Test"), item.get("status", "Not supplied"), details or "—"])
        if len(journey_rows) > 1:
            story.append(make_table(journey_rows, [48*mm, 26*mm, 100*mm]))
        else:
            story.append(para("Journey report exists but contains no test result rows."))
    else:
        story.append(para("No browser journey JSON report was available when this report was generated."))

    story.append(Paragraph("Keyboard navigation audit", styles["SectionHeading"]))
    if keyboard_data:
        story.append(para(
            f"Keyboard test URL: {keyboard_data.get('url', 'Not recorded')} · "
            f"Focusable elements visited: {len(focus_items)}"
        ))
        focus_rows = [["Tab order", "Element", "Accessible hint", "Focus visible"]]
        for idx, item in enumerate(focus_items, start=1):
            if not isinstance(item, dict):
                continue
            hint = item.get("aria_label") or item.get("text") or item.get("id") or item.get("href") or "No label captured"
            focus_rows.append([idx, item.get("tag", ""), str(hint)[:100], "Yes" if item.get("focus_visible") is True else "Not detected"])
        if len(focus_rows) > 1:
            story.append(make_table(focus_rows, [20*mm, 25*mm, 92*mm, 37*mm]))
        reverse = keyboard_data.get("reverse_navigation")
        if isinstance(reverse, dict):
            reverse_hint = reverse.get("aria_label") or reverse.get("text") or reverse.get("id") or reverse.get("tag") or "Unknown"
            story.append(para(f"Shift + Tab target: {reverse_hint} · Focus visible: {'Yes' if reverse.get('focus_visible') is True else 'Not detected'}"))
    else:
        story.append(para("No keyboard navigation JSON report was available when this report was generated."))

    story.append(Paragraph("Methodology and limitations", styles["SectionHeading"]))
    story.append(para(
        "WebDoc combines an automated axe-core scan, Gemini-generated explanations and "
        "remediation suggestions, and Playwright browser checks. Automated results do not "
        "prove full WCAG conformance. The journey module checks homepage loading, page title, "
        "up to 10 navigation links, and button/form counts. The keyboard module records up to "
        "30 Tab focus stops and one Shift+Tab target. These tests do not complete a checkout, "
        "submit forms, test every route, or replace manual testing with assistive technologies. "
        "AI suggestions require developer review and a fresh scan before deployment.",
        limit=1600,
    ))

    def add_page_number(canvas, document):
        canvas.saveState()
        page_w, _ = A4
        canvas.setStrokeColor(colors.HexColor("#D8E2EA"))
        canvas.line(17*mm, 13*mm, page_w - 17*mm, 13*mm)
        canvas.setFont("Helvetica", 7)
        canvas.setFillColor(muted)
        canvas.drawString(17*mm, 8*mm, "WebDoc · AI Website Accessibility Doctor")
        canvas.drawRightString(page_w - 17*mm, 8*mm, f"Page {document.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    return buffer.getvalue()


def build_full_report_html(scan_data, ai_data, journey_data, keyboard_data):
    """Accessible HTML fallback when ReportLab is not installed."""
    from html import escape
    import json as _json

    sections = []
    for title, data in [
        ("Accessibility scan", scan_data),
        ("Gemini AI analysis", ai_data),
        ("Browser journey audit", journey_data),
        ("Keyboard navigation audit", keyboard_data),
    ]:
        if data:
            pretty = escape(_json.dumps(data, ensure_ascii=False, indent=2))
            sections.append(f"<section><h2>{escape(title)}</h2><pre>{pretty}</pre></section>")
        else:
            sections.append(f"<section><h2>{escape(title)}</h2><p>No report data available.</p></section>")
    return ("<!doctype html><html lang='en'><meta charset='utf-8'><title>WebDoc Full Audit Report</title>"
            "<style>body{font:15px/1.6 Arial,sans-serif;max-width:1050px;margin:40px auto;padding:0 24px;color:#18334b}"
            "h1,h2{color:#173f60}section{margin:30px 0;padding:20px;border:1px solid #d7e4ef;border-radius:12px}"
            "pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#f4f8fc;padding:14px;border-radius:8px;font-size:12px}"
            "@media print{body{margin:12mm auto}section{break-inside:avoid}}</style><body>"
            "<h1>WebDoc — Full Accessibility Audit Report</h1>"
            f"<p>Generated: {escape(__import__('datetime').datetime.now().isoformat(timespec='seconds'))}</p>"
            + "".join(sections) + "</body></html>")


def render_full_report_download():
    """Render the same full-report export on Dashboard and Journey pages."""
    scan_data = load_latest_scan_data()
    ai_data = read_optional_json(AI_RESULTS_FILE)
    journey_data = read_optional_json(PROJECT_DIR / "data" / "journey_results.json")
    keyboard_data = read_optional_json(PROJECT_DIR / "data" / "keyboard_results.json")

    if not any((scan_data, ai_data, journey_data, keyboard_data)):
        st.info("Run a website scan or Journey audit before exporting a report.")
        return

    website = (
        (scan_data or {}).get("final_url")
        or (scan_data or {}).get("url")
        or (journey_data or {}).get("url")
        or (keyboard_data or {}).get("url")
        or "website"
    )
    safe_site = re.sub(r"[^A-Za-z0-9.-]+", "_", urlparse(website).hostname or "website")
    report_date = __import__("datetime").datetime.now().strftime("%Y%m%d_%H%M")

    st.markdown("### Export your WebDoc audit")
    st.caption("One report containing the latest scan findings, Gemini guidance, journey checks and keyboard-focus results available on this device.")
    try:
        pdf_bytes = build_full_report_pdf(scan_data, ai_data, journey_data, keyboard_data)
        st.download_button(
            "⬇  Download Full Report (PDF)",
            data=pdf_bytes,
            file_name=f"WebDoc_Accessibility_Report_{safe_site}_{report_date}.pdf",
            mime="application/pdf",
            type="primary",
            width="stretch",
            key=f"wd_full_report_pdf_{st.session_state.get('wd_page', 'page')}",
        )
    except ImportError:
        html_report = build_full_report_html(scan_data, ai_data, journey_data, keyboard_data)
        st.download_button(
            "⬇  Download Full Report (HTML)",
            data=html_report.encode("utf-8"),
            file_name=f"WebDoc_Accessibility_Report_{safe_site}_{report_date}.html",
            mime="text/html",
            type="primary",
            width="stretch",
            key=f"wd_full_report_html_{st.session_state.get('wd_page', 'page')}",
        )
        st.info("PDF export needs ReportLab. Install it with: python -m pip install reportlab. HTML report export is available now.")


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

        render_full_report_download()
        st.divider()

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
    page_heading(
        "USER IMPACT",
        "Accessibility <span>profiles.</span>",
        "Explore how detected accessibility barriers may affect different users.",
    )

    # Use the same latest persisted scan as Dashboard and WCAG Issues.
    scan_data = load_latest_scan_data()

    if not isinstance(scan_data, dict):
        st.info("No scan results are available yet. Go to Home and analyse a website first.")
    else:
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

        # Map only rule IDs actually returned by the scanner. These mappings
        # indicate potential relevance, not confirmed impact on an individual.
        profile_definitions = [
            {
                "name": "Blind users",
                "description": (
                    "Screen-reader users rely on language metadata, accessible "
                    "control names, meaningful links and semantic page structure."
                ),
                "rules": {
                    "html-has-lang": "Language metadata helps screen readers pronounce content correctly.",
                    "label": "Form controls need accessible labels.",
                    "link-name": "Links need discernible names that communicate their purpose.",
                    "list": "Lists should use valid semantic list structure.",
                    "region": "Landmarks help screen-reader users navigate page sections.",
                },
            },
            {
                "name": "Low-vision users",
                "description": (
                    "Sufficient text and interface contrast can make content easier to perceive."
                ),
                "rules": {
                    "color-contrast": "The scanner found foreground/background combinations below its contrast threshold.",
                },
            },
            {
                "name": "Colour-blind users",
                "description": (
                    "Contrast can support readability. This scan does not establish "
                    "whether information is communicated by colour alone."
                ),
                "rules": {
                    "color-contrast": "Low contrast may make some text or interface content harder to distinguish.",
                },
            },
            {
                "name": "Deaf and hard-of-hearing users",
                "description": (
                    "Captions and text alternatives help make audio and video content accessible."
                ),
                "rules": {},
            },
            {
                "name": "Keyboard-only users",
                "description": (
                    "Keyboard users need operable controls, visible focus and a logical focus order."
                ),
                "rules": {},
            },
            {
                "name": "Cognitive and reading needs",
                "description": (
                    "Language metadata, clear control labels, descriptive links and semantic "
                    "grouping can make content easier to understand and navigate."
                ),
                "rules": {
                    "html-has-lang": "Language metadata helps assistive technology identify the page language.",
                    "label": "Clear form labels help users identify the purpose of controls.",
                    "link-name": "Meaningful link names help users understand link purpose.",
                    "list": "Semantic lists help organise related information.",
                },
            },
        ]

        issue_lookup = {}
        for issue in violations:
            if isinstance(issue, dict) and issue.get("id"):
                issue_lookup[str(issue["id"])] = issue

        st.info(
            "These cards show potential relevance based on detected rule IDs. "
            "They do not measure individual user impact or certify that a profile "
            "has no accessibility barriers. A profile with no mapped findings "
            "means this scan did not return a directly mapped rule."
        )

        profile_cols = st.columns(3, gap="medium")
        for index, profile in enumerate(profile_definitions):
            matched_issues = []
            reported_affected_nodes = 0

            for rule_id, relevance_note in profile["rules"].items():
                issue = issue_lookup.get(rule_id)
                if issue is None:
                    continue

                nodes = issue.get("nodes")
                if not isinstance(nodes, list):
                    nodes = []

                try:
                    affected_count = int(issue.get("affected_nodes"))
                except (TypeError, ValueError):
                    affected_count = len(nodes)

                affected_count = max(0, affected_count)
                reported_affected_nodes += affected_count
                matched_issues.append((issue, relevance_note, affected_count))

            with profile_cols[index % 3]:
                with st.container(border=True):
                    st.markdown(f"### {profile['name']}")
                    st.write(profile["description"])

                    metric_cols = st.columns(2)
                    metric_cols[0].metric(
                        "Relevant rules",
                        len(matched_issues),
                    )
                    metric_cols[1].metric(
                        "Reported affected nodes*",
                        reported_affected_nodes,
                    )

                    if matched_issues:
                        st.markdown("**Related scan findings**")
                        for issue, relevance_note, affected_count in matched_issues:
                            issue_title = issue.get("help") or issue.get("id") or "Accessibility issue"
                            severity = str(issue.get("impact") or "Unknown").title()
                            st.markdown(f"- **{issue_title}** · {severity} · {affected_count} nodes")
                            st.caption(relevance_note)
                    else:
                        st.info(
                            "No directly mapped violations were detected for this "
                            "profile in the current scan. This is not proof of full accessibility."
                        )

        st.caption(
            "*Affected-node counts are summed across matched rules. The same page "
            "element may be counted under multiple rules or profiles."
        )

elif selected_page == "Heatmap":

    page_heading(
        "VISUAL DIAGNOSIS",
        "Accessibility <span>heatmap.</span>",
        "Locate detected issues visually and inspect the affected page elements."
    )

    scan_data = load_latest_scan_data()

    if not isinstance(scan_data, dict):

        st.info("Run a website scan first to generate a screenshot and element coordinates.")

    else:

        violations = scan_data.get("violations", [])

        if not isinstance(violations, list):
            violations = []

        screenshot_value = (
            scan_data.get("screenshot")
            or "data/website_screenshot.png"
        )

        screenshot_path = Path(screenshot_value)

        if not screenshot_path.is_absolute():
            screenshot_path = PROJECT_DIR / screenshot_path

        if not screenshot_path.exists():

            st.error(f"Website screenshot not found: {screenshot_path}")

        else:

            try:
                from PIL import Image, ImageDraw

                with Image.open(screenshot_path) as source_image:
                    screenshot = source_image.convert("RGBA")

            except Exception as exc:

                st.error(f"Could not open website screenshot: {exc}")
                screenshot = None

            if screenshot is not None:

                metadata = scan_data.get("screenshot_metadata") or {}

                try:
                    css_width = float(
                        metadata.get("css_width") or screenshot.width
                    )
                    css_height = float(
                        metadata.get("css_height") or screenshot.height
                    )

                except (TypeError, ValueError):

                    css_width = screenshot.width
                    css_height = screenshot.height

                scale_x = (
                    screenshot.width / css_width
                    if css_width > 0 else 1.0
                )

                scale_y = (
                    screenshot.height / css_height
                    if css_height > 0 else 1.0
                )

                severity_colours = {
                    "critical": (210, 45, 58, 255),
                    "serious": (238, 128, 35, 255),
                    "moderate": (218, 174, 45, 255),
                    "minor": (48, 125, 190, 255)
                }

                severity_col, rule_col = st.columns(2)

                with severity_col:

                    severity_filter = st.selectbox(
                        "Filter by severity",
                        [
                            "All",
                            "Critical",
                            "Serious",
                            "Moderate",
                            "Minor"
                        ],
                        key="heatmap_severity_filter"
                    )

                available_rules = [
                    str(issue.get("id"))
                    for issue in violations
                    if isinstance(issue, dict) and issue.get("id")
                ]

                with rule_col:

                    rule_filter = st.selectbox(
                        "Filter by rule",
                        ["All rules"] + available_rules,
                        key="heatmap_rule_filter"
                    )

                markers = []

                for issue in violations:

                    if not isinstance(issue, dict):
                        continue

                    issue_id = str(issue.get("id") or "unknown")

                    severity = str(
                        issue.get("impact") or "minor"
                    ).lower()

                    if (
                        severity_filter != "All"
                        and severity != severity_filter.lower()
                    ):
                        continue

                    if (
                        rule_filter != "All rules"
                        and issue_id != rule_filter
                    ):
                        continue

                    nodes = issue.get("nodes") or []

                    if not isinstance(nodes, list):
                        continue

                    for node in nodes:

                        if not isinstance(node, dict):
                            continue

                        box = node.get("bounding_box")

                        if not isinstance(box, dict):
                            continue

                        try:
                            x = float(box["x"])
                            y = float(box["y"])
                            width = float(box["width"])
                            height = float(box["height"])

                        except (KeyError, TypeError, ValueError):
                            continue

                        if width <= 0 or height <= 0:
                            continue

                        targets = node.get("target") or []

                        if isinstance(targets, str):
                            targets = [targets]

                        markers.append({
                            "issue_id": issue_id,
                            "title": issue.get("help") or issue_id,
                            "severity": severity,
                            "description": issue.get("description") or "",
                            "html": node.get("html") or "",
                            "failure": node.get("failure_summary") or "",
                            "selector": " → ".join(
                                str(target) for target in targets
                            ),
                            "box": (x, y, width, height)
                        })

                all_nodes = [
                    node
                    for issue in violations
                    if isinstance(issue, dict)
                    for node in (issue.get("nodes") or [])
                    if isinstance(node, dict)
                ]

                located_count = sum(
                    1
                    for node in all_nodes
                    if isinstance(node.get("bounding_box"), dict)
                )

                st.caption(
                    f"Website: {scan_data.get('final_url') or scan_data.get('url') or 'URL not recorded'}"
                )

                metric_cols = st.columns(3)

                metric_cols[0].metric(
                    "Detected rules",
                    len(violations)
                )

                metric_cols[1].metric(
                    "Located elements",
                    located_count
                )

                metric_cols[2].metric(
                    "Unlocated elements",
                    max(0, len(all_nodes) - located_count)
                )

                if not markers:

                    st.warning(
                        "No elements match these filters or have captured coordinates. "
                        "Run a fresh scan with the updated scanner."
                    )

                    st.image(
                        screenshot.convert("RGB"),
                        caption="Website screenshot",
                        width="stretch"
                    )

                else:

                    selected_index = st.selectbox(
                        "Choose a numbered finding",
                        range(len(markers)),
                        format_func=lambda index: (
                            f"#{index + 1} | "
                            f"{markers[index]['severity'].title()} | "
                            f"{markers[index]['issue_id']} | "
                            f"{markers[index]['selector'][:55]}"
                        ),
                        key="heatmap_selected_index"
                    )

                    overlay = screenshot.copy()

                    marker_layer = Image.new(
                        "RGBA",
                        overlay.size,
                        (0, 0, 0, 0)
                    )

                    draw = ImageDraw.Draw(marker_layer)

                    for index, marker in enumerate(markers):

                        x, y, width, height = marker["box"]

                        left = max(
                            0,
                            min(
                                int(x * scale_x),
                                overlay.width - 1
                            )
                        )

                        top = max(
                            0,
                            min(
                                int(y * scale_y),
                                overlay.height - 1
                            )
                        )

                        right = max(
                            left + 1,
                            min(
                                int((x + width) * scale_x),
                                overlay.width - 1
                            )
                        )

                        bottom = max(
                            top + 1,
                            min(
                                int((y + height) * scale_y),
                                overlay.height - 1
                            )
                        )

                        colour = severity_colours.get(
                            marker["severity"],
                            (48, 125, 190, 255)
                        )

                        line_width = (
                            7 if index == selected_index else 3
                        )

                        if index == selected_index:
                            colour = (35, 175, 110, 255)

                        draw.rectangle(
                            (left, top, right, bottom),
                            outline=colour,
                            width=line_width
                        )

                        radius = 13

                        dot_right = min(
                            left + radius * 2,
                            overlay.width - 1
                        )

                        dot_bottom = min(
                            top + radius * 2,
                            overlay.height - 1
                        )

                        draw.ellipse(
                            (
                                left,
                                top,
                                dot_right,
                                dot_bottom
                            ),
                            fill=colour,
                            outline=(255, 255, 255, 255),
                            width=2
                        )

                        draw.text(
                            (left + 7, top + 5),
                            str(index + 1),
                            fill=(255, 255, 255, 255)
                        )

                    overlay = Image.alpha_composite(
                        overlay,
                        marker_layer
                    ).convert("RGB")

                    st.subheader("Website issue map")

                    st.image(
                        overlay,
                        caption=(
                            "Red: Critical | Orange: Serious | "
                            "Gold: Moderate | Blue: Minor | "
                            "Green: Selected"
                        ),
                        width="stretch"
                    )

                    selected = markers[selected_index]

                    st.divider()

                    st.subheader(selected["title"])

                    detail_cols = st.columns(2)

                    detail_cols[0].metric(
                        "Severity",
                        selected["severity"].title()
                    )

                    detail_cols[1].metric(
                        "Rule ID",
                        selected["issue_id"]
                    )

                    st.caption(
                        "CSS selector: "
                        + (selected["selector"] or "Not supplied")
                    )

                    if selected["description"]:
                        st.write(selected["description"])

                    if selected["html"]:

                        with st.expander("Affected HTML"):

                            st.code(
                                selected["html"],
                                language="html"
                            )

                    if selected["failure"]:

                        with st.expander("Scanner failure details"):

                            st.text(selected["failure"])

                    # Connect the selected issue to Gemini results.

                    if AI_RESULTS_FILE.exists():

                        try:

                            with AI_RESULTS_FILE.open(
                                "r",
                                encoding="utf-8"
                            ) as file:

                                ai_data = json.load(file)

                            ai_results = (
                                ai_data.get("results", [])
                                if isinstance(ai_data, dict)
                                else []
                            )

                            ai_match = next(
                                (
                                    item
                                    for item in ai_results
                                    if isinstance(item, dict)
                                    and item.get("issue_id") == selected["issue_id"]
                                    and isinstance(item.get("analysis"), dict)
                                ),
                                None
                            )

                            if ai_match:

                                analysis = ai_match["analysis"]

                                with st.container(border=True):

                                    st.markdown(
                                        "**Gemini explanation and remediation**"
                                    )

                                    st.write(
                                        analysis.get("explanation")
                                        or "No explanation available."
                                    )

                                    if analysis.get("recommended_fix"):

                                        st.markdown("**Recommended fix**")

                                        st.write(
                                            analysis["recommended_fix"]
                                        )

                                    if analysis.get("wcag_reference"):

                                        st.caption(
                                            "WCAG reference: "
                                            + str(analysis["wcag_reference"])
                                        )

                            else:

                                st.info(
                                    "No Gemini explanation is saved for this rule yet."
                                )

                        except (OSError, json.JSONDecodeError) as exc:

                            st.warning(
                                f"Could not read Gemini analysis: {exc}"
                            )

                st.caption(
                    "Markers use captured DOM coordinates. Some nodes inside "
                    "inaccessible frames or unresolved shadow targets may not "
                    "have a position. Re-scan after website changes."
                )


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
    from html import escape as html_escape

    page_heading(
        "AI REMEDIATION STUDIO",
        "See the fix. <span>before it ships.</span>",
        "A visual review space for comparing the scanned HTML with Gemini's suggested correction.",
    )

    # Always load the newest persisted scan and AI analysis.
    scan_data = load_latest_scan_data()
    ai_data = None
    if AI_RESULTS_FILE.exists():
        try:
            with AI_RESULTS_FILE.open("r", encoding="utf-8") as file:
                loaded_ai = json.load(file)
            if isinstance(loaded_ai, dict):
                ai_data = loaded_ai
        except (json.JSONDecodeError, OSError) as exc:
            st.error(f"Could not read AI analysis results: {exc}")

    ai_results = ai_data.get("results", []) if isinstance(ai_data, dict) else []
    if not isinstance(ai_results, list):
        ai_results = []

    failed_results = [
        item for item in ai_results
        if isinstance(item, dict)
        and (item.get("status") == "failed" or item.get("error"))
    ]

    # Only offer corrections that contain actual generated HTML.
    preview_candidates = []
    for item in ai_results:
        if not isinstance(item, dict):
            continue
        analysis = item.get("analysis")
        if not isinstance(analysis, dict):
            continue
        patch = item.get("patch")
        if not isinstance(patch, dict):
            patch = {}
        corrected = patch.get("corrected_code") or analysis.get("corrected_code") or ""
        if isinstance(corrected, str) and corrected.strip():
            preview_candidates.append(item)

    if not preview_candidates:
        st.html("""
        <div style="padding:26px;border:1px solid var(--wd-border);border-radius:20px;
                    background:linear-gradient(135deg,var(--wd-surface),var(--wd-surface2));">
          <div style="font-size:11px;font-weight:850;letter-spacing:1.5px;color:var(--wd-accent);">REMEDIATION WORKSPACE</div>
          <div style="font-size:23px;font-weight:850;color:var(--wd-text);margin:8px 0;">Your fix preview will appear here</div>
          <div style="font-size:13px;line-height:1.7;color:var(--wd-muted);max-width:650px;">
            Run a fresh website analysis and wait for Gemini to return a corrected HTML fragment.
            WebDoc will place the original and suggested version side by side for review.
          </div>
        </div>
        """)
        if failed_results:
            quota_limited = any(
                "429" in str(item.get("error", ""))
                or "RESOURCE_EXHAUSTED" in str(item.get("error", ""))
                for item in failed_results
            )
            if quota_limited:
                st.warning("Gemini's request quota/rate limit was reached. No sample fix is substituted; the preview waits for a real generated correction.")
            else:
                st.warning("The latest AI analysis contains failed requests, so no generated correction is ready to preview.")
            st.caption(f"Failed AI analyses: {len(failed_results)}")
        else:
            st.info("No generated HTML correction is available yet. Run a website scan first.")
    else:
        def preview_option_label(item):
            analysis = item.get("analysis") or {}
            issue_id = item.get("issue_id") or "Accessibility issue"
            problem = analysis.get("problem") or "Generated HTML correction"
            return f"{issue_id}  ·  {problem}"

        pick_col, hint_col = st.columns([3, 2], vertical_alignment="bottom")
        with pick_col:
            selected_preview_index = st.selectbox(
                "Select an AI-generated fix",
                range(len(preview_candidates)),
                format_func=lambda index: preview_option_label(preview_candidates[index]),
                key="preview_issue_index",
            )
        with hint_col:
            st.caption("Choose a finding to load its original and corrected HTML.")

        selected_item = preview_candidates[selected_preview_index]
        selected_analysis = selected_item.get("analysis") or {}
        selected_patch = selected_item.get("patch") or {}
        selected_issue_id = selected_item.get("issue_id") or "unknown-rule"
        original_code = selected_patch.get("original_code") or ""
        corrected_code = selected_patch.get("corrected_code") or selected_analysis.get("corrected_code") or ""
        validation = selected_patch.get("validation") or {}
        verification_status = selected_patch.get("verification_status") or "not provided"
        patch_applicable = selected_patch.get("patch_applicable")
        human_review_required = selected_patch.get("human_review_required")
        if human_review_required is None:
            human_review_required = selected_analysis.get("human_review_required")

        if not original_code and isinstance(scan_data, dict):
            for violation in scan_data.get("violations", []):
                if not isinstance(violation, dict) or violation.get("id") != selected_issue_id:
                    continue
                nodes = violation.get("nodes") or []
                if nodes and isinstance(nodes[0], dict):
                    original_code = nodes[0].get("html") or ""
                break

        issue_title = selected_analysis.get("problem") or selected_analysis.get("issue_title") or selected_issue_id.replace("-", " ").title()
        explanation = (
            selected_analysis.get("why_it_matters")
            or selected_analysis.get("explanation")
            or selected_analysis.get("user_impact")
            or selected_analysis.get("description")
            or "This correction is intended to address the selected accessibility finding. Review the rendered result and verify it with a fresh scan."
        )
        fix_summary = (
            selected_analysis.get("recommendation")
            or selected_analysis.get("suggested_fix")
            or selected_analysis.get("fix_explanation")
            or "Review the suggested HTML correction below before applying it to the source website."
        )

        is_valid = validation.get("valid") is True
        severity = str(selected_item.get("impact") or selected_analysis.get("severity") or "Review").title()
        status_text = "Static checks passed" if is_valid else ("Static checks failed" if validation.get("valid") is False else "Validation unavailable")
        status_tone = "#20865A" if is_valid else ("#B76B17" if validation.get("valid") is False else "#647C91")

        st.html(f"""
        <div style="border:1px solid var(--wd-border);border-radius:22px;overflow:hidden;
                    background:linear-gradient(120deg,var(--wd-surface),var(--wd-surface2));margin:8px 0 18px;">
          <div style="padding:22px 24px 18px;display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;align-items:flex-start;">
            <div style="max-width:720px;">
              <div style="font-size:10px;letter-spacing:1.6px;font-weight:850;color:var(--wd-accent);">SELECTED ACCESSIBILITY FINDING</div>
              <div style="font-size:25px;font-weight:850;letter-spacing:-.8px;color:var(--wd-text);margin:7px 0 5px;">{html_escape(str(issue_title))}</div>
              <div style="font-size:12px;color:var(--wd-muted);">Rule ID · <code>{html_escape(str(selected_issue_id))}</code></div>
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;">
              <span style="padding:7px 11px;border-radius:30px;background:var(--wd-soft);border:1px solid var(--wd-border);font-size:10px;font-weight:800;color:var(--wd-text);">{html_escape(severity)} impact</span>
              <span style="padding:7px 11px;border-radius:30px;background:var(--wd-surface);border:1px solid var(--wd-border);font-size:10px;font-weight:800;color:{status_tone};">● {html_escape(status_text)}</span>
            </div>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr;gap:1px;background:var(--wd-border);border-top:1px solid var(--wd-border);">
            <div style="background:var(--wd-surface);padding:16px 22px;"><div style="font-size:9px;font-weight:850;letter-spacing:1.2px;color:var(--wd-muted);">WHY IT MATTERS</div><div style="font-size:12px;line-height:1.7;color:var(--wd-text);margin-top:6px;">{html_escape(str(explanation))[:650]}</div></div>
            <div style="background:var(--wd-surface);padding:16px 22px;"><div style="font-size:9px;font-weight:850;letter-spacing:1.2px;color:var(--wd-muted);">AI FIX STRATEGY</div><div style="font-size:12px;line-height:1.7;color:var(--wd-text);margin-top:6px;">{html_escape(str(fix_summary))[:650]}</div></div>
          </div>
        </div>
        """)

        meta_cols = st.columns(3)
        meta_cols[0].metric("Static validation", "Passed" if is_valid else "Review")
        meta_cols[1].metric("Verification", str(verification_status).replace("_", " ").title())
        meta_cols[2].metric("Human review", "Required" if human_review_required else "Recommended")

        if patch_applicable is False:
            st.warning("This patch is not marked for automatic application. The preview is for inspection only.")
        elif patch_applicable is True:
            st.info("The patch passed its applicability check, but it is not verified until a fresh accessibility scan confirms the result.")
        if validation.get("valid") is not True:
            st.warning("The corrected preview is shown for inspection, not as an approved production-ready change.")

        def render_browser_preview(fragment, title, mode):
            """Render a static fragment inside a sandboxed, script-disabled browser frame."""
            safe_fragment = fragment if fragment else "<p class='empty'>No HTML fragment was captured for this side.</p>"
            document = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; img-src data:; font-src data:; frame-src 'none'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
*{{box-sizing:border-box}} body{{margin:0;background:#f2f5fa;color:#172b42;font-family:Inter,Arial,sans-serif;padding:14px;overflow-wrap:anywhere}}
.browser{{background:#fff;border:1px solid #dbe3ee;border-radius:13px;overflow:hidden;box-shadow:0 8px 24px rgba(23,45,74,.08)}}
.chrome{{height:37px;display:flex;align-items:center;gap:6px;padding:0 12px;background:#f8fafc;border-bottom:1px solid #e7edf4}}
.dot{{width:8px;height:8px;border-radius:50%;background:#cbd5e1}} .address{{margin-left:8px;background:#edf2f7;border-radius:5px;height:17px;flex:1;max-width:230px}}
.preview-label{{font-size:9px;font-weight:800;letter-spacing:1px;color:#75859a;margin:0 0 10px}}
.site{{padding:22px;min-height:235px;background:#fff}} .site h1,.site h2,.site h3{{color:#173f60;line-height:1.2}} .site p,.site li{{line-height:1.65;color:#34495e;font-size:14px}}
.site button{{border:0;border-radius:7px;background:#173f60;color:#fff;padding:10px 15px;font-weight:700}}
.site a{{color:#1769aa;text-decoration:underline}} .site img{{max-width:100%;height:auto}} .site input,.site select{{padding:8px;border:1px solid #aab8c8;border-radius:5px}}
.site *{{max-width:100%}} .empty{{padding:20px;border:1px dashed #cbd5e1;border-radius:8px;color:#64748b}}
form,button,a,input,select,textarea{{pointer-events:none}}
</style></head><body>
<div class="preview-label">{html_escape(mode.upper())} · STATIC SANDBOX</div>
<div class="browser"><div class="chrome"><i class="dot"></i><i class="dot"></i><i class="dot"></i><div class="address"></div></div><main class="site">{safe_fragment}</main></div>
</body></html>"""
            srcdoc = html_escape(document, quote=True)
            iframe = (
                f'<iframe title="{html_escape(title, quote=True)}" sandbox="" '
                'referrerpolicy="no-referrer" '
                'style="display:block;width:100%;height:330px;border:0;border-radius:14px;background:#f2f5fa" '
                f'srcdoc="{srcdoc}"></iframe>'
            )
            st.iframe(iframe, height=340)

        st.markdown("## Visual comparison")
        st.caption("The two panels render the supplied HTML fragments in isolated browser frames. This is a focused component preview, not a pixel-perfect copy of the live website.")
        before_col, after_col = st.columns(2, gap="large")
        with before_col:
            with st.container(border=True):
                st.html('<div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-size:10px;font-weight:850;letter-spacing:1.2px;color:var(--wd-muted);">01 / CURRENT STATE</span><span style="font-size:10px;font-weight:800;color:#B64C53;">● ISSUE DETECTED</span></div><div style="font-size:19px;font-weight:850;color:var(--wd-text);margin:7px 0 2px;">Before</div><div style="font-size:11px;color:var(--wd-muted);">Original scanner-captured markup</div>')
                render_browser_preview(original_code, "Original HTML fragment", "Before")
                with st.expander("Inspect original HTML"):
                    if original_code:
                        st.code(str(original_code)[:12000], language="html")
                    else:
                        st.info("The scanner did not provide an original HTML fragment for this rule.")
        with after_col:
            with st.container(border=True):
                st.html('<div style="display:flex;justify-content:space-between;align-items:center;"><span style="font-size:10px;font-weight:850;letter-spacing:1.2px;color:var(--wd-muted);">02 / PROPOSED STATE</span><span style="font-size:10px;font-weight:800;color:#20865A;">● AI SUGGESTION</span></div><div style="font-size:19px;font-weight:850;color:var(--wd-text);margin:7px 0 2px;">After</div><div style="font-size:11px;color:var(--wd-muted);">Gemini-generated corrected markup</div>')
                if is_valid:
                    render_browser_preview(corrected_code, "Corrected HTML fragment", "After")
                else:
                    st.info("Corrected visual preview is withheld because static validation did not pass.")
                with st.expander("Inspect suggested HTML"):
                    st.code(str(corrected_code)[:12000], language="html")

        st.html("""
        <div style="margin-top:14px;padding:17px 20px;border:1px solid var(--wd-border);border-radius:16px;background:var(--wd-surface);">
          <div style="font-size:10px;font-weight:850;letter-spacing:1.3px;color:var(--wd-accent);">REVIEW BEFORE RELEASE</div>
          <div style="font-size:13px;line-height:1.75;color:var(--wd-text);margin-top:7px;">
            WebDoc does not push changes to the live website. A developer should review the HTML, apply the change in the source project, and run a fresh accessibility scan to verify the outcome.
          </div>
        </div>
        """)


elif selected_page == "Journey":
    page_heading(
        "KEYBOARD & INTERACTION AUDIT",
        "Can every user <span>move through it?</span>",
        "Run a real browser-based journey and keyboard-focus audit on the website you scanned.",
    )

    scan_data = load_latest_scan_data()
    suggested_url = (
        (scan_data.get("final_url") or scan_data.get("url"))
        if isinstance(scan_data, dict)
        else ""
    ) or st.session_state.get("wd_url", "")

    journey_json = PROJECT_DIR / "data" / "journey_results.json"
    keyboard_json = PROJECT_DIR / "data" / "keyboard_results.json"
    journey_script = PROJECT_DIR / "scanner" / "journey_tester.py"
    keyboard_script = PROJECT_DIR / "scanner" / "keyboard_test.py"

    st.html("""
    <div style="padding:22px 24px;border:1px solid var(--wd-border);border-radius:20px;
                background:linear-gradient(120deg,var(--wd-surface),var(--wd-surface2));margin:10px 0 18px;">
      <div style="font-size:10px;font-weight:850;letter-spacing:1.5px;color:var(--wd-accent);">REAL BROWSER TESTING</div>
      <div style="font-size:22px;font-weight:850;color:var(--wd-text);margin:7px 0;">Follow the page. Follow the focus.</div>
      <div style="font-size:12px;line-height:1.75;color:var(--wd-muted);max-width:760px;">
        WebDoc opens the target in Chrome, checks page loading and basic navigation elements,
        then records the keyboard Tab sequence and reverse Shift+Tab focus target.
      </div>
    </div>
    """)

    with st.form("wd_journey_run_form"):
        journey_url_input = st.text_input(
            "Website to test",
            value=suggested_url,
            placeholder="https://yourwebsite.com",
        )
        run_journey = st.form_submit_button(
            "▶  Run journey + keyboard audit",
            type="primary",
            width="stretch",
        )

    if run_journey:
        target_url = normalise_url(journey_url_input)
        if not target_url:
            st.error("Enter a valid website URL before starting the audit.")
        elif not journey_script.exists() or not keyboard_script.exists():
            missing = []
            if not journey_script.exists():
                missing.append("scanner/journey_tester.py")
            if not keyboard_script.exists():
                missing.append("scanner/keyboard_test.py")
            st.error("Journey test module(s) not found: " + ", ".join(missing))
            st.caption("The Journey page expects the Playwright test modules in the scanner folder.")
        else:
            run_errors = []
            run_logs = []
            audit_commands = [
                (
                    "Browser journey audit",
                    "from scanner.journey_tester import test_user_journey; "
                    f"test_user_journey({target_url!r})",
                    journey_json,
                ),
                (
                    "Keyboard navigation audit",
                    "from scanner.keyboard_test import test_keyboard_navigation; "
                    f"test_keyboard_navigation({target_url!r})",
                    keyboard_json,
                ),
            ]

            for label, code, expected_output in audit_commands:
                with st.spinner(f"Running {label.lower()} in Chrome..."):
                    try:
                        process = subprocess.run(
                            [sys.executable, "-c", code],
                            cwd=str(PROJECT_DIR),
                            capture_output=True,
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            timeout=240,
                        )
                        run_logs.append(
                            f"=== {label} ===\n"
                            + (process.stdout or "")
                            + (process.stderr or "")
                        )
                        if process.returncode != 0:
                            run_errors.append(
                                f"{label} failed: "
                                + ((process.stderr or process.stdout or "Unknown error")[-2500:])
                            )
                        elif not expected_output.exists():
                            run_errors.append(
                                f"{label} finished but did not create {expected_output.name}."
                            )
                    except subprocess.TimeoutExpired:
                        run_errors.append(f"{label} timed out after 240 seconds.")
                    except OSError as exc:
                        run_errors.append(f"Could not start {label}: {exc}")

            st.session_state.wd_journey_run_url = target_url
            st.session_state.wd_journey_run_errors = run_errors
            st.session_state.wd_journey_run_logs = run_logs
            st.session_state.wd_journey_run_timestamp = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()

    previous_errors = st.session_state.get("wd_journey_run_errors", [])
    if previous_errors:
        for message in previous_errors:
            st.error(message)
    elif st.session_state.get("wd_journey_run_timestamp"):
        st.success("Both browser audits completed. The latest JSON reports are loaded below.")

    if st.session_state.get("wd_journey_run_timestamp"):
        st.caption(
            "Last run: "
            + str(st.session_state.wd_journey_run_timestamp)
            + " · Website: "
            + str(st.session_state.get("wd_journey_run_url", ""))
        )

    def read_journey_json(path):
        if not path.exists():
            return None
        try:
            with path.open("r", encoding="utf-8") as result_file:
                data = json.load(result_file)
            return data if isinstance(data, dict) else None
        except (OSError, json.JSONDecodeError) as exc:
            st.warning(f"Could not read {path.name}: {exc}")
            return None

    journey_data = read_journey_json(journey_json)
    keyboard_data = read_journey_json(keyboard_json)

    if journey_data is None and keyboard_data is None:
        st.info("No journey audit report is available yet. Enter a website above and run the audit.")
    else:
        st.markdown("## Journey overview")
        journey_results = journey_data.get("results", []) if journey_data else []
        if not isinstance(journey_results, list):
            journey_results = []

        links = [
            item for item in journey_results
            if isinstance(item, dict) and item.get("step") == "Check navigation link"
        ]
        page_load = next(
            (item for item in journey_results if isinstance(item, dict) and item.get("step") == "Open homepage"),
            {},
        )
        title_check = next(
            (item for item in journey_results if isinstance(item, dict) and item.get("step") == "Check page title"),
            {},
        )
        button_check = next(
            (item for item in journey_results if isinstance(item, dict) and item.get("step") == "Check buttons"),
            {},
        )
        form_check = next(
            (item for item in journey_results if isinstance(item, dict) and item.get("step") == "Check forms"),
            {},
        )

        keyboard_items = keyboard_data.get("focused_elements", []) if keyboard_data else []
        if not isinstance(keyboard_items, list):
            keyboard_items = []
        visible_focus_count = sum(
            1 for item in keyboard_items
            if isinstance(item, dict) and item.get("focus_visible") is True
        )
        reverse_focus = keyboard_data.get("reverse_navigation") if keyboard_data else None

        overview_cols = st.columns(4)
        overview_cols[0].metric(
            "Homepage load",
            "Passed" if page_load.get("status") == "passed" else ("Failed" if page_load else "—"),
        )
        overview_cols[1].metric("Navigation links found", len(links))
        overview_cols[2].metric("Keyboard focus stops", len(keyboard_items))
        overview_cols[3].metric("Visible focus states", visible_focus_count)

        st.divider()
        left_panel, right_panel = st.columns(2, gap="large")

        with left_panel:
            with st.container(border=True):
                st.markdown("### Browser journey checks")
                if journey_data:
                    st.caption(journey_data.get("url", "URL not recorded"))
                    if page_load:
                        if page_load.get("status") == "passed":
                            st.success("Homepage loaded successfully")
                        else:
                            st.error("Homepage load failed")
                            if page_load.get("error"):
                                st.caption(str(page_load["error"])[:500])
                    if title_check:
                        if title_check.get("status") == "passed":
                            st.success("Page title present")
                            st.write(f"**Title:** {title_check.get('title', '')}")
                        else:
                            st.warning("Page title is missing")
                    c1, c2 = st.columns(2)
                    c1.metric("Buttons inventoried", button_check.get("total_buttons", "—"))
                    c2.metric("Forms inventoried", form_check.get("total_forms", "—"))
                else:
                    st.info("Journey report is not available yet.")

        with right_panel:
            with st.container(border=True):
                st.markdown("### Keyboard navigation")
                if keyboard_data:
                    st.metric("Focusable elements visited", len(keyboard_items))
                    st.metric("Elements reporting :focus-visible", visible_focus_count)
                    if isinstance(reverse_focus, dict):
                        reverse_name = (
                            reverse_focus.get("aria_label")
                            or reverse_focus.get("text")
                            or reverse_focus.get("id")
                            or reverse_focus.get("tag")
                            or "Unknown element"
                        )
                        st.write(f"**Shift + Tab returned to:** {reverse_name}")
                        if reverse_focus.get("focus_visible") is True:
                            st.success("Reverse focus target reports a visible keyboard focus state")
                        else:
                            st.warning("Reverse focus target did not report :focus-visible")
                else:
                    st.info("Keyboard report is not available yet.")

        st.divider()
        st.markdown("## Navigation link inventory")
        if links:
            link_rows = []
            for item in links:
                link_rows.append({
                    "Link text": item.get("link_text") or "(no visible text captured)",
                    "Destination": item.get("href") or "(href missing)",
                    "Result": "Found in DOM",
                })
            st.dataframe(link_rows, width="stretch", hide_index=True)
        elif journey_data:
            st.info("No anchor links were found among the first 10 links inspected by the journey script.")

        st.markdown("## Keyboard focus sequence")
        if keyboard_items:
            focus_rows = []
            for index, item in enumerate(keyboard_items, start=1):
                if not isinstance(item, dict):
                    continue
                accessible_hint = (
                    item.get("aria_label")
                    or item.get("text")
                    or item.get("id")
                    or item.get("href")
                    or "(no text or label captured)"
                )
                focus_rows.append({
                    "Tab order": index,
                    "Element": str(item.get("tag", "")).lower(),
                    "Accessible hint": str(accessible_hint)[:120],
                    "Focus visible": "Yes" if item.get("focus_visible") is True else "Not detected",
                    "ID": item.get("id") or "—",
                })
            st.dataframe(focus_rows, width="stretch", hide_index=True)
        elif keyboard_data:
            st.info("No focusable elements were recorded during the Tab test.")

        st.caption(
            "Scope note: the current journey script checks homepage loading, page title, "
            "up to 10 navigation links, and counts buttons/forms. The keyboard script records "
            "up to 30 Tab focus stops and one Shift+Tab target. It does not complete a checkout, "
            "submit forms, test every route, or replace manual assistive-technology testing."
        )

    saved_logs = st.session_state.get("wd_journey_run_logs", [])
    if saved_logs:
        with st.expander("View browser test logs"):
            for log_item in saved_logs:
                st.code(log_item[-6000:])

    st.divider()
    render_full_report_download()


st.divider()
st.markdown("<div class='wd-footer'><strong>WebDoc · AI Website Accessibility Doctor</strong><span>Building a more inclusive digital world.</span></div>", unsafe_allow_html=True)