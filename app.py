# from pathlib import Path
# from urllib.parse import urlparse

# import streamlit as st

# # ============================================================
# # WEBDOC | AI WEBSITE ACCESSIBILITY DOCTOR
# # Single-file frontend MVP with working page navigation + theme switch
# # ============================================================

# st.set_page_config(
#     page_title="WebDoc | AI Accessibility Doctor",
#     page_icon="W",
#     layout="wide",
#     initial_sidebar_state="collapsed",
# )

# # ---------------------------
# # State
# # ---------------------------
# if "wd_dark_mode" not in st.session_state:
#     st.session_state.wd_dark_mode = False
# if "wd_page" not in st.session_state:
#     st.session_state.wd_page = "Home"
# if "wd_url" not in st.session_state:
#     st.session_state.wd_url = ""

# # ---------------------------
# # Theme toggle is rendered BEFORE choosing the palette.
# # Streamlit reruns the script after the user changes it.
# # ---------------------------
# brand_col, nav_col, theme_col = st.columns([1.25, 4.4, 1.15], vertical_alignment="center")
# with brand_col:
#     st.html(
#         """
#         <div class="wd-brand">
#           <div class="wd-logo">W</div>
#           <div><div class="wd-brand-name">WebDoc</div>
#           <div class="wd-brand-subtitle">ACCESSIBILITY INTELLIGENCE</div></div>
#         </div>
#         """
#     )

# PAGES = ["Home", "Dashboard", "WCAG Issues", "Profiles", "Heatmap", "AI Co-Pilot", "Preview", "Journey"]
# with nav_col:
#     selected_page = st.radio(
#         "Main navigation",
#         PAGES,
#         horizontal=True,
#         key="wd_page",
#         label_visibility="collapsed",
#     )
# with theme_col:
#     st.toggle("Dark mode", key="wd_dark_mode")

# # ---------------------------
# # Palette
# # ---------------------------
# DARK = st.session_state.wd_dark_mode
# if DARK:
#     C = {
#         "bg": "#100D14", "surface": "#1D1722", "surface2": "#241B2B",
#         "primary": "#492D55", "accent": "#EA8DB8", "text": "#F5EFF7",
#         "muted": "#B9AABD", "soft": "#302337", "border": "#3A3040",
#         "input": "#17111C", "button_text": "#241725", "button": "#EA8DB8",
#         "visual1": "#492D55", "visual2": "#24162B", "glow": "rgba(234,141,184,.16)",
#         "success": "#86D5B0", "warning": "#F2C078", "danger": "#F08C91"
#     }
# else:
#     C = {
#         "bg": "#F4F8FC", "surface": "#FFFFFF", "surface2": "#EAF3FA",
#         "primary": "#173F60", "accent": "#F17F73", "text": "#18334B",
#         "muted": "#647C91", "soft": "#EAF3FA", "border": "#D7E4EF",
#         "input": "#FFFFFF", "button_text": "#FFFFFF", "button": "#173F60",
#         "visual1": "#173F60", "visual2": "#102C43", "glow": "rgba(59,130,180,.14)",
#         "success": "#237C5A", "warning": "#A96818", "danger": "#BD424B"
#     }

# # ---------------------------
# # Theme-aware CSS
# # ---------------------------
# CSS = """
# <style>
# :root {
#  --wd-bg: __BG__; --wd-surface: __SURFACE__; --wd-surface2: __SURFACE2__;
#  --wd-primary: __PRIMARY__; --wd-accent: __ACCENT__; --wd-text: __TEXT__;
#  --wd-muted: __MUTED__; --wd-soft: __SOFT__; --wd-border: __BORDER__;
#  --wd-input: __INPUT__; --wd-button-text: __BUTTON_TEXT__; --wd-button: __BUTTON__;
#  --wd-visual1: __VISUAL1__; --wd-visual2: __VISUAL2__; --wd-glow: __GLOW__;
#  --wd-success: __SUCCESS__; --wd-warning: __WARNING__; --wd-danger: __DANGER__;
# }
# html { scroll-behavior: smooth; }
# html, body, .stApp, [data-testid="stAppViewContainer"],
# [data-testid="stMain"], [data-testid="stMainBlockContainer"] {
#  background: var(--wd-bg) !important; color: var(--wd-text) !important;
# }
# [data-testid="stHeader"] { background: transparent !important; }
# [data-testid="stMainBlockContainer"] {
#  max-width: 1500px !important; padding: 1.35rem clamp(1rem, 3.5vw, 3.5rem) 3.5rem !important;
# }
# /* Brand */
# .wd-brand { min-height: 52px; display:flex; align-items:center; gap:11px; }
# .wd-logo { width:43px; height:43px; display:grid; place-items:center; border-radius:14px;
#  background:var(--wd-primary); color:#fff; font-size:22px; font-weight:850;
#  box-shadow:0 8px 24px var(--wd-glow); }
# .wd-brand-name { color:var(--wd-text); font-size:23px; font-weight:850; letter-spacing:-.8px; line-height:1.1; }
# .wd-brand-subtitle { color:var(--wd-muted); font-size:8px; font-weight:750; letter-spacing:1.4px; margin-top:4px; white-space:nowrap; }
# /* Actual Streamlit radio navigation */
# div[data-testid="stRadio"] > label { display:none !important; }
# div[data-testid="stRadio"] div[role="radiogroup"] { display:flex; flex-wrap:wrap; justify-content:center; gap:5px; }
# div[data-testid="stRadio"] div[role="radiogroup"] label {
#  background:transparent; border:1px solid transparent; border-radius:10px; padding:7px 10px;
#  color:var(--wd-muted) !important; transition:all .15s ease; margin:0 !important;
# }
# div[data-testid="stRadio"] div[role="radiogroup"] label p { color:inherit !important; font-size:12px; font-weight:650; }
# div[data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {
#  background:var(--wd-soft); border-color:var(--wd-border); color:var(--wd-text) !important;
# }
# div[data-testid="stRadio"] div[role="radiogroup"] label > div:first-child { display:none !important; }
# [data-testid="stToggle"] label, [data-testid="stToggle"] p { color:var(--wd-text) !important; font-size:12px !important; font-weight:650 !important; }
# /* Shared components */
# .wd-rule { height:1px; background:var(--wd-border); margin:22px 0 28px; }
# .wd-eyebrow, .wd-kicker { color:var(--wd-accent); font-size:10px; font-weight:850; letter-spacing:1.8px; }
# .wd-eyebrow { display:inline-block; padding:9px 14px; border:1px solid var(--wd-border); border-radius:30px; background:var(--wd-soft); margin-bottom:22px; }
# .wd-hero { padding:36px 8px 30px 0; }
# .wd-hero h1 { max-width:680px; margin:0 0 20px; color:var(--wd-text); font-size:clamp(42px,5.2vw,70px); font-weight:850; line-height:1.06; letter-spacing:-3px; }
# .wd-hero h1 span, .wd-title span { color:var(--wd-accent); }
# .wd-copy { color:var(--wd-muted); font-size:15px; line-height:1.85; max-width:550px; }
# .wd-pills { display:flex; flex-wrap:wrap; gap:8px; margin-top:22px; }
# .wd-pills span { padding:8px 12px; border:1px solid var(--wd-border); border-radius:30px; background:var(--wd-soft); color:var(--wd-text); font-size:10px; font-weight:700; }
# .wd-note { color:var(--wd-muted); font-size:11px; margin-top:25px; }
# [data-testid="stVerticalBlockBorderWrapper"] { background:var(--wd-surface) !important; border:1px solid var(--wd-border) !important; border-radius:20px !important; box-shadow:0 12px 38px var(--wd-glow); }
# .wd-panel-label { color:var(--wd-muted); font-size:9px; font-weight:800; letter-spacing:1.4px; }
# .wd-panel-title { color:var(--wd-text); font-size:23px; font-weight:820; letter-spacing:-.7px; margin-top:6px; }
# .wd-visual { margin:16px 0; padding:17px; border-radius:16px; color:#fff; background:radial-gradient(circle at 85% 12%,var(--wd-glow),transparent 38%),linear-gradient(135deg,var(--wd-visual1),var(--wd-visual2)); }
# .wd-visual-top { display:flex; justify-content:space-between; color:rgba(255,255,255,.75); font-size:9px; font-weight:750; letter-spacing:1.1px; }
# .wd-visual-main { display:flex; align-items:center; gap:15px; padding:22px 0; }
# .wd-orbit { width:70px; height:70px; flex:0 0 70px; display:grid; place-items:center; border:1px solid rgba(255,255,255,.4); border-radius:50%; box-shadow:0 0 0 8px rgba(255,255,255,.05); }
# .wd-orbit b { display:grid; place-items:center; width:48px; height:48px; border-radius:50%; background:var(--wd-accent); color:var(--wd-button-text); font-size:21px; }
# .wd-visual strong { color:#fff; font-size:14px; }
# .wd-visual p { color:rgba(255,255,255,.76); font-size:10px; line-height:1.6; margin:5px 0 0; }
# .wd-visual-row { display:flex; justify-content:space-between; border-top:1px solid rgba(255,255,255,.17); padding:9px 0; color:#fff; font-size:10px; }
# .wd-visual-row span:last-child { opacity:.75; }
# .wd-title { color:var(--wd-text); font-size:clamp(26px,3vw,38px); line-height:1.2; font-weight:850; letter-spacing:-1.3px; margin:10px 0; }
# .wd-subtitle { color:var(--wd-muted); font-size:13px; line-height:1.75; max-width:680px; }
# .wd-card-label { color:var(--wd-accent); font-size:10px; font-weight:850; letter-spacing:1.2px; }
# .wd-card-title { color:var(--wd-text); font-size:17px; font-weight:800; margin:16px 0 8px; }
# .wd-card-copy { color:var(--wd-muted); font-size:12px; line-height:1.8; }
# .wd-number { color:var(--wd-accent); font-size:25px; font-weight:850; }
# .wd-footer { display:flex; justify-content:space-between; flex-wrap:wrap; gap:12px; color:var(--wd-muted); font-size:11px; padding:12px 0; }
# /* Widgets */
# [data-testid="stTextInput"] input, [data-testid="stTextArea"] textarea, [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
#  background:var(--wd-input) !important; color:var(--wd-text) !important; border-color:var(--wd-border) !important; border-radius:10px !important;
# }
# [data-testid="stTextInput"] label, [data-testid="stSelectbox"] label, [data-testid="stWidgetLabel"] p { color:var(--wd-text) !important; }
# .stButton button, [data-testid="stFormSubmitButton"] button, [data-testid="stDownloadButton"] button {
#  background:var(--wd-button) !important; color:var(--wd-button-text) !important; border:0 !important; border-radius:10px !important; font-weight:800 !important; min-height:42px;
# }
# [data-testid="stMetric"] { background:var(--wd-surface); border:1px solid var(--wd-border); border-radius:15px; padding:14px; }
# [data-testid="stMetricLabel"] p { color:var(--wd-muted) !important; }
# [data-testid="stMetricValue"] { color:var(--wd-text) !important; }
# [data-testid="stDataFrame"] { border:1px solid var(--wd-border); border-radius:12px; }
# [data-testid="stAlert"] { border-radius:12px; }
# @media(max-width:900px) { .wd-hero h1 { font-size:46px; letter-spacing:-2px; } }
# @media(max-width:600px) { .wd-hero h1 { font-size:38px; letter-spacing:-1px; } .wd-footer { flex-direction:column; } }
# </style>
# """

# repls = {
#     "__BG__": C["bg"], "__SURFACE__": C["surface"], "__SURFACE2__": C["surface2"],
#     "__PRIMARY__": C["primary"], "__ACCENT__": C["accent"], "__TEXT__": C["text"],
#     "__MUTED__": C["muted"], "__SOFT__": C["soft"], "__BORDER__": C["border"],
#     "__INPUT__": C["input"], "__BUTTON_TEXT__": C["button_text"], "__BUTTON__": C["button"],
#     "__VISUAL1__": C["visual1"], "__VISUAL2__": C["visual2"], "__GLOW__": C["glow"],
#     "__SUCCESS__": C["success"], "__WARNING__": C["warning"], "__DANGER__": C["danger"],
# }
# for old, new in repls.items():
#     CSS = CSS.replace(old, new)
# st.html(CSS)

# # ---------------------------
# # Small reusable UI helpers
# # ---------------------------
# def page_heading(kicker: str, title: str, subtitle: str):
#     st.html(
#         f'<div class="wd-kicker">{kicker}</div>'
#         f'<div class="wd-title">{title}</div>'
#         f'<div class="wd-subtitle">{subtitle}</div>'
#     )


# def info_card(number: str, title: str, copy: str, tag: str = ""):
#     with st.container(border=True):
#         st.html(
#             f'<div class="wd-card-label">{number} {tag}</div>'
#             f'<div class="wd-card-title">{title}</div>'
#             f'<div class="wd-card-copy">{copy}</div>'
#         )

# # ---------------------------
# # HOME
# # ---------------------------
# if selected_page == "Home":
#     left, right = st.columns([1.08, 0.92], gap="large", vertical_alignment="center")
#     with left:
#         st.html(
#             """
#             <section class="wd-hero">
#               <div class="wd-eyebrow">INTELLIGENT WEB ACCESSIBILITY</div>
#               <h1>The web should<br>work for <span>everyone.</span></h1>
#               <p class="wd-copy">Your website deserves more than a basic accessibility score. Discover barriers, understand who they affect, and create a better digital experience with AI-powered guidance.</p>
#               <div class="wd-pills"><span>WCAG analysis</span><span>AI remediation</span><span>Inclusive design</span></div>
#               <div class="wd-note">A smarter way to build an inclusive web.</div>
#             </section>
#             """
#         )
#     with right:
#         with st.container(border=True):
#             st.html(
#                 """
#                 <div class="wd-panel-label">YOUR ACCESSIBILITY WORKSPACE</div>
#                 <div class="wd-panel-title">Start with a scan.</div>
#                 <div class="wd-visual">
#                   <div class="wd-visual-top"><span>WEBSITE DIAGNOSTICS</span><span>WEBDOC / 01</span></div>
#                   <div class="wd-visual-main"><div class="wd-orbit"><b>W</b></div><div><strong>Every detail matters.</strong><p>Understand your website from every user's perspective.</p></div></div>
#                   <div class="wd-visual-row"><span>01 / Page structure</span><span>Ready to check</span></div>
#                   <div class="wd-visual-row"><span>02 / Visual accessibility</span><span>Ready to check</span></div>
#                   <div class="wd-visual-row"><span>03 / Keyboard access</span><span>Ready to check</span></div>
#                 </div>
#                 <div class="wd-card-title">Enter your website URL</div>
#                 <div class="wd-card-copy">We'll analyse the page and identify accessibility barriers.</div>
#                 """
#             )
#             with st.form("website_scan_form", clear_on_submit=False):
#                 url_input = st.text_input("Website URL", value=st.session_state.wd_url, placeholder="https://yourwebsite.com", label_visibility="collapsed")
#                 scan_submit = st.form_submit_button("Analyse website", use_container_width=True)
#             if scan_submit:
#                 candidate = url_input.strip()
#                 if candidate and "://" not in candidate:
#                     candidate = "https://" + candidate
#                 parsed = urlparse(candidate)
#                 if not parsed.hostname or parsed.scheme not in ("http", "https"):
#                     st.error("Enter a valid public website URL, such as https://example.com.")
#                 else:
#                     st.session_state.wd_url = candidate
#                     st.session_state.wd_page = "Dashboard"
#                     st.success("URL saved. The scanner module can now be connected by the team.")
#                     st.rerun()

#     st.html('<div class="wd-rule"></div>')
#     metrics = st.columns(3)
#     for col, value, label in zip(metrics, ["06", "WCAG", "AI"], ["ACCESSIBILITY PERSPECTIVES", "GUIDED ANALYSIS", "INTELLIGENT REMEDIATION"]):
#         with col:
#             st.html(f'<div class="wd-number">{value}</div><div class="wd-card-copy">{label}</div>')
#     st.html('<div class="wd-rule"></div>')
#     page_heading("WHAT WE DO", "From accessibility barriers <span>to better experiences.</span>", "Understand, improve and verify website accessibility in one workspace.")
#     feature_cols = st.columns(3, gap="medium")
#     for col, data in zip(feature_cols, [
#         ("01", "Intelligent diagnosis", "Detect accessibility violations and understand how they affect real users.", "DETECT"),
#         ("02", "AI-powered remediation", "Get clear explanations and practical HTML/CSS fixes for accessibility problems.", "IMPROVE"),
#         ("03", "Verified improvements", "Compare original and corrected pages and verify improvements with a fresh scan.", "VERIFY"),
#     ]):
#         with col:
#             info_card(data[0], data[1], data[2], data[3])
#     st.html('<div class="wd-rule"></div>')
#     page_heading("THE WEBDOC PROCESS", "Three steps towards <span>an inclusive web.</span>", "Diagnose the issue, understand its impact, then verify the fix.")
#     step_cols = st.columns(3)
#     for col, data in zip(step_cols, [("01", "Diagnose", "Scan a website and discover accessibility barriers."), ("02", "Understand", "See who is affected and prioritise the problems."), ("03", "Transform", "Generate fixes and verify improvements.")]):
#         with col:
#             info_card(data[0], data[1], data[2])

# # ---------------------------
# # DASHBOARD
# # ---------------------------
# elif selected_page == "Dashboard":
#     page_heading("OVERVIEW", "Accessibility <span>dashboard.</span>", "A central view of scan health, detected issues and recommended next steps.")
#     if st.session_state.wd_url:
#         st.caption(f"Current website: {st.session_state.wd_url}")
#     else:
#         st.info("No website has been submitted yet. Go to Home to enter a URL. The metrics below are demonstration placeholders.")
#     metric_cols = st.columns(4)
#     for col, label, value, delta in zip(metric_cols, ["Accessibility score", "Total issues", "Critical issues", "Profiles affected"], ["72/100", "15", "3", "4/6"], ["Demo value", "Demo value", "Demo value", "Demo value"]):
#         with col:
#             st.metric(label, value, delta)
#     st.subheader("Issue distribution")
#     chart_cols = st.columns([1.15, 0.85])
#     with chart_cols[0]:
#         st.bar_chart({"Issues": [3, 5, 4, 3]}, x_label="Severity", y_label="Count")
#     with chart_cols[1]:
#         with st.container(border=True):
#             st.markdown("**Recommended next steps**")
#             st.write("1. Review critical issues")
#             st.write("2. Check keyboard navigation")
#             st.write("3. Verify AI-generated fixes")

# # ---------------------------
# # WCAG ISSUES
# # ---------------------------
# elif selected_page == "WCAG Issues":
#     page_heading("DIAGNOSIS", "WCAG <span>issues.</span>", "Review detected barriers, their severity and the WCAG criteria they relate to.")
#     demo_issues = [
#         {"Issue": "Button has no accessible name", "WCAG": "4.1.2", "Severity": "Serious", "Affected element": "button.checkout"},
#         {"Issue": "Image is missing alternative text", "WCAG": "1.1.1", "Severity": "Critical", "Affected element": "img.hero-image"},
#         {"Issue": "Text contrast is too low", "WCAG": "1.4.3", "Severity": "Serious", "Affected element": "p.description"},
#         {"Issue": "Form control has no label", "WCAG": "1.3.1", "Severity": "Moderate", "Affected element": "input.email"},
#     ]
#     st.caption("Demonstration data — replace with Person 1's scanner output during integration.")
#     st.dataframe(demo_issues, use_container_width=True, hide_index=True)

# # ---------------------------
# # PROFILES
# # ---------------------------
# elif selected_page == "Profiles":
#     page_heading("USER IMPACT", "Accessibility <span>profiles.</span>", "Understand how barriers can affect people with different access needs.")
#     profile_data = [
#         ("Blind users", "Screen-reader labels, landmarks and semantic structure.", 65),
#         ("Low-vision users", "Contrast, text resizing and magnification.", 72),
#         ("Colour-blind users", "Colour-independent cues and visual distinctions.", 78),
#         ("Deaf and hard-of-hearing users", "Captions and alternatives to audio.", 86),
#         ("Keyboard-only users", "Focus visibility and keyboard operability.", 60),
#         ("Cognitive and reading needs", "Clear structure, language and predictable interactions.", 81),
#     ]
#     cols = st.columns(3, gap="medium")
#     for col, (name, desc, score) in zip(cols * 2, profile_data):
#         with col:
#             with st.container(border=True):
#                 st.markdown(f"**{name}**")
#                 st.progress(score / 100)
#                 st.caption(f"Illustrative profile score: {score}/100")
#                 st.write(desc)

# # ---------------------------
# # HEATMAP
# # ---------------------------
# elif selected_page == "Heatmap":
#     page_heading("VISUAL DIAGNOSIS", "Accessibility <span>heatmap.</span>", "Locate detected issues visually and inspect the affected page elements.")
#     st.info("The visual overlay will become interactive when Person 1's scanner supplies a screenshot and element selectors. This screen currently shows the integration placeholder.")
#     with st.container(border=True):
#         st.markdown("**Detected element markers — sample data**")
#         for label, selector, severity in [("Missing image alternative text", "img.hero-image", "Critical"), ("Button accessible name", "button.checkout", "Serious"), ("Low text contrast", "p.description", "Moderate")]:
#             st.write(f"{severity}  ·  `{selector}`  ·  {label}")

# # ---------------------------
# # AI CO-PILOT
# # ---------------------------
# elif selected_page == "AI Co-Pilot":
#     page_heading("AI REMEDIATION", "Your accessibility <span>co-pilot.</span>", "Get understandable explanations and practical code suggestions for selected issues.")
#     issue = st.selectbox("Choose a sample issue", ["Button has no accessible name", "Image is missing alternative text", "Low text contrast"])
#     explanations = {
#         "Button has no accessible name": ("A screen reader may announce this as an unnamed button, leaving users unsure what it does.", '<button type="submit" aria-label="Submit checkout">Continue</button>'),
#         "Image is missing alternative text": ("People using screen readers may not receive the information conveyed by this meaningful image.", '<img src="product.jpg" alt="Blue running shoes viewed from the side">'),
#         "Low text contrast": ("Some users may struggle to read text that does not have sufficient contrast against its background.", '/* Choose foreground and background colours that meet the applicable WCAG contrast ratio. */'),
#     }
#     explanation, patch = explanations[issue]
#     with st.container(border=True):
#         st.markdown("**What is the problem?**")
#         st.write(explanation)
#         st.markdown("**Example correction**")
#         st.code(patch, language="html")
#     st.caption("Sample guidance only. Gemini API integration and context-aware patch generation will be connected by Person 2.")

# # ---------------------------
# # BEFORE / AFTER PREVIEW
# # ---------------------------
# elif selected_page == "Preview":
#     page_heading("REMEDIATION", "Before & <span>after.</span>", "Compare the original page with a temporary corrected preview.")
#     before, after = st.columns(2)
#     with before:
#         with st.container(border=True):
#             st.markdown("**Original example**")
#             st.code('<button></button>', language="html")
#             st.error("Accessible name missing")
#     with after:
#         with st.container(border=True):
#             st.markdown("**Corrected example**")
#             st.code('<button aria-label="Submit">Submit</button>', language="html")
#             st.success("Accessible name added — still requires re-scan verification")
#     st.caption("The preview will use Person 2's patch output and a sandboxed rendering step.")

# # ---------------------------
# # JOURNEY TESTER
# # ---------------------------
# elif selected_page == "Journey":
#     page_heading("INTERACTION TESTING", "Accessibility <span>journey.</span>", "Check whether a keyboard-only user can complete a key task on a website.")
#     journey = [("1", "Open homepage", "Passed"), ("2", "Move to product search", "Passed"), ("3", "Open product details", "Passed"), ("4", "Add item to cart", "Needs testing"), ("5", "Continue to checkout", "Not reached")]
#     for number, label, result in journey:
#         with st.container(border=True):
#             a, b = st.columns([3, 1])
#             with a:
#                 st.markdown(f"**Step {number}: {label}**")
#             with b:
#                 st.caption(result)
#     st.caption("Sample journey only. Person 1's keyboard and journey test module will provide real results.")

# # ---------------------------
# # Footer
# # ---------------------------
# st.divider()
# st.markdown("<div class='wd-footer'><strong>WebDoc · AI Website Accessibility Doctor</strong><span>Building a more inclusive digital world.</span></div>", unsafe_allow_html=True)


























import re
from urllib.parse import urlparse

import streamlit as st

# ============================================================
# WEBDOC | AI WEBSITE ACCESSIBILITY DOCTOR
# Single-file frontend MVP with working page navigation + theme switch
# ============================================================

st.set_page_config(
    page_title="WebDoc | AI Accessibility Doctor",
    page_icon="W",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------
# URL validation
# ---------------------------
HOSTNAME_RE = re.compile(
    r"^(?=.{1,253}$)([A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}$"
)


def normalise_url(raw):
    """Return a cleaned http(s) URL, or None if the input is not valid."""
    candidate = raw.strip()
    if not candidate or any(ch.isspace() for ch in candidate):
        return None

    if "://" not in candidate:
        # Reject things like javascript:... or mailto:..., but allow host:port
        if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", candidate) and not re.match(
            r"^[^/]+:\d+(/|$)", candidate
        ):
            return None
        candidate = "https://" + candidate

    try:
        parsed = urlparse(candidate)
        hostname = parsed.hostname
        parsed.port  # raises ValueError for an invalid port
    except ValueError:
        return None

    if parsed.scheme not in ("http", "https") or not hostname:
        return None
    if parsed.username or parsed.password:
        return None
    if not HOSTNAME_RE.match(hostname):
        return None
    return candidate


# ---------------------------
# State
# ---------------------------
if "wd_dark_mode" not in st.session_state:
    st.session_state.wd_dark_mode = False
if "wd_page" not in st.session_state:
    st.session_state.wd_page = "Home"
if "wd_url" not in st.session_state:
    st.session_state.wd_url = ""

# A page change requested later in the script (e.g. after a successful scan
# form submit) is stored here and applied BEFORE the nav radio is created.
# Streamlit does not allow changing a widget's key after it has been created.
if "wd_goto" in st.session_state:
    st.session_state.wd_page = st.session_state.pop("wd_goto")

# ---------------------------
# Theme toggle is rendered BEFORE choosing the palette.
# Streamlit reruns the script after the user changes it.
# ---------------------------
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

# ---------------------------
# Palette
# ---------------------------
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

# ---------------------------
# Theme-aware CSS
# ---------------------------
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
/* FIX: Streamlit's fixed header (~60px, very high z-index) used to sit on top of
   the nav and the dark-mode toggle and swallow every click. Push the content
   below it. */
[data-testid="stMainBlockContainer"] {
 max-width: 1500px !important; padding: 4.5rem clamp(1rem, 3.5vw, 3.5rem) 3.5rem !important;
}
/* Native Streamlit text must follow the theme too (otherwise it stays dark on dark) */
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li, [data-testid="stHeading"],
h1, h2, h3, h4, h5, h6 { color: var(--wd-text) !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p { color: var(--wd-muted) !important; }
/* Brand */
.wd-brand { min-height: 52px; display:flex; align-items:center; gap:11px; }
.wd-logo { width:43px; height:43px; display:grid; place-items:center; border-radius:14px;
 background:var(--wd-primary); color:#fff; font-size:22px; font-weight:850;
 box-shadow:0 8px 24px var(--wd-glow); }
.wd-brand-name { color:var(--wd-text); font-size:23px; font-weight:850; letter-spacing:-.8px; line-height:1.1; }
.wd-brand-subtitle { color:var(--wd-muted); font-size:8px; font-weight:750; letter-spacing:1.4px; margin-top:4px; white-space:nowrap; }
/* Actual Streamlit radio navigation */
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
/* hide the round radio indicator so the options look like tabs */
div[data-testid="stRadio"] [data-testid="stRadioOption"] > div > div:first-child:not([data-testid]) { display:none !important; }
/* In current Streamlit the toggle is rendered as a "stCheckbox" element */
[data-testid="stToggle"] label, [data-testid="stToggle"] p,
[data-testid="stCheckbox"] label, [data-testid="stCheckbox"] p {
 color:var(--wd-text) !important; font-size:12px !important; font-weight:650 !important;
}
/* Shared components */
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
/* Button labels keep their own contrast colour (must come after the generic text rule) */
.stButton button p, [data-testid="stFormSubmitButton"] button p, [data-testid="stDownloadButton"] button p,
.stButton button [data-testid="stMarkdownContainer"] p, [data-testid="stFormSubmitButton"] button [data-testid="stMarkdownContainer"] p {
 color:var(--wd-button-text) !important;
}
/* Widgets */
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

# ---------------------------
# Small reusable UI helpers
# ---------------------------
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

# ---------------------------
# HOME
# ---------------------------
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
                    st.error("Enter a valid public website URL, such as https://example.com.")
                else:
                    st.session_state.wd_url = candidate
                    # FIX: cannot assign to the radio's key here (widget already exists).
                    # Queue the change; it is applied at the top of the next run.
                    st.session_state.wd_goto = "Dashboard"
                    st.rerun()

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

# ---------------------------
# DASHBOARD
# ---------------------------
elif selected_page == "Dashboard":
    page_heading("OVERVIEW", "Accessibility <span>dashboard.</span>", "A central view of scan health, detected issues and recommended next steps.")
    if st.session_state.wd_url:
        st.caption(f"Current website: {st.session_state.wd_url}")
    else:
        st.info("No website has been submitted yet. Go to Home to enter a URL. The metrics below are demonstration placeholders.")
    metric_cols = st.columns(4)
    for col, label, value, delta in zip(metric_cols, ["Accessibility score", "Total issues", "Critical issues", "Profiles affected"], ["72/100", "15", "3", "4/6"], ["Demo value", "Demo value", "Demo value", "Demo value"]):
        with col:
            st.metric(label, value, delta)
    st.subheader("Issue distribution")
    chart_cols = st.columns([1.15, 0.85])
    with chart_cols[0]:
        st.bar_chart({"Issues": [3, 5, 4, 3]}, x_label="Severity", y_label="Count")
    with chart_cols[1]:
        with st.container(border=True):
            st.markdown("**Recommended next steps**")
            st.write("1. Review critical issues")
            st.write("2. Check keyboard navigation")
            st.write("3. Verify AI-generated fixes")

# ---------------------------
# WCAG ISSUES
# ---------------------------
elif selected_page == "WCAG Issues":
    page_heading("DIAGNOSIS", "WCAG <span>issues.</span>", "Review detected barriers, their severity and the WCAG criteria they relate to.")
    demo_issues = [
        {"Issue": "Button has no accessible name", "WCAG": "4.1.2", "Severity": "Serious", "Affected element": "button.checkout"},
        {"Issue": "Image is missing alternative text", "WCAG": "1.1.1", "Severity": "Critical", "Affected element": "img.hero-image"},
        {"Issue": "Text contrast is too low", "WCAG": "1.4.3", "Severity": "Serious", "Affected element": "p.description"},
        {"Issue": "Form control has no label", "WCAG": "1.3.1", "Severity": "Moderate", "Affected element": "input.email"},
    ]
    st.caption("Demonstration data — replace with Person 1's scanner output during integration.")
    st.dataframe(demo_issues, width="stretch", hide_index=True)

# ---------------------------
# PROFILES
# ---------------------------
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

# ---------------------------
# HEATMAP
# ---------------------------
elif selected_page == "Heatmap":
    page_heading("VISUAL DIAGNOSIS", "Accessibility <span>heatmap.</span>", "Locate detected issues visually and inspect the affected page elements.")
    st.info("The visual overlay will become interactive when Person 1's scanner supplies a screenshot and element selectors. This screen currently shows the integration placeholder.")
    with st.container(border=True):
        st.markdown("**Detected element markers — sample data**")
        for label, selector, severity in [("Missing image alternative text", "img.hero-image", "Critical"), ("Button accessible name", "button.checkout", "Serious"), ("Low text contrast", "p.description", "Moderate")]:
            st.write(f"{severity}  ·  `{selector}`  ·  {label}")

# ---------------------------
# AI CO-PILOT
# ---------------------------
elif selected_page == "AI Co-Pilot":
    page_heading("AI REMEDIATION", "Your accessibility <span>co-pilot.</span>", "Get understandable explanations and practical code suggestions for selected issues.")
    issue = st.selectbox("Choose a sample issue", ["Button has no accessible name", "Image is missing alternative text", "Low text contrast"])
    explanations = {
        "Button has no accessible name": ("A screen reader may announce this as an unnamed button, leaving users unsure what it does.", '<button type="submit" aria-label="Submit checkout">Continue</button>'),
        "Image is missing alternative text": ("People using screen readers may not receive the information conveyed by this meaningful image.", '<img src="product.jpg" alt="Blue running shoes viewed from the side">'),
        "Low text contrast": ("Some users may struggle to read text that does not have sufficient contrast against its background.", '/* Choose foreground and background colours that meet the applicable WCAG contrast ratio. */'),
    }
    explanation, patch = explanations[issue]
    with st.container(border=True):
        st.markdown("**What is the problem?**")
        st.write(explanation)
        st.markdown("**Example correction**")
        st.code(patch, language="html")
    st.caption("Sample guidance only. Gemini API integration and context-aware patch generation will be connected by Person 2.")

# ---------------------------
# BEFORE / AFTER PREVIEW
# ---------------------------
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

# ---------------------------
# JOURNEY TESTER
# ---------------------------
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

# ---------------------------
# Footer
# ---------------------------
st.divider()
st.markdown("<div class='wd-footer'><strong>WebDoc · AI Website Accessibility Doctor</strong><span>Building a more inclusive digital world.</span></div>", unsafe_allow_html=True)
