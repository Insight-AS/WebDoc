# Person 2 — AI Co-Pilot module

This folder contains the starter implementation for the AI portion of **AI Website Accessibility Doctor**.

## What is included

- `ai_helper.py` — sends one scanner issue to Gemini and returns a Pydantic-validated explanation plus proposed HTML.
- `remediation.py` — performs basic static checks on generated HTML and packages a patch for preview/re-scan.
- `test_ai.py` — manual live Gemini smoke test using the sample issue.
- `examples/sample_issue.json` — sample input that can be used before Person 1 finishes the scanner.
- `tests/test_remediation.py` — local tests that do not need an API key.
- `.env.example` — template for the secret API key.

## 1. Setup

Run these commands from the project root in a terminal.

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and set your own `GEMINI_API_KEY`. Get the key from Google AI Studio: https://aistudio.google.com/app/apikey

**Never upload `.env` or share your API key in chat/GitHub.** `.gitignore` is included to prevent accidental commits.

## 2. Test without spending API calls

```bash
python -m unittest discover -s tests -v
```

## 3. Test the Gemini integration

```bash
python test_ai.py
```

This sends `examples/sample_issue.json` to Gemini. A successful response includes:

- problem
- affected_users
- explanation
- wcag_reference
- recommended_fix
- corrected_code
- verification_steps
- human_review_required

The model is configurable through `GEMINI_MODEL` in `.env`. The default is `gemini-3.8-flash`.

## 4. How Person 3 can call this module

```python
from ai_helper import generate_accessibility_analysis

analysis = generate_accessibility_analysis(issue, language="English")
st.error(analysis["explanation"])  # or display with st.write
st.code(analysis["corrected_code"], language="html")
```

## 5. How to prepare a patch package

```python
from ai_helper import generate_accessibility_analysis
from remediation import build_patch_package

analysis = generate_accessibility_analysis(issue, language="English")
patch_package = build_patch_package(issue, analysis)
print(patch_package)
```

`verification_status` remains `pending_rescan` until Person 1's scanner re-tests the corrected preview. Static validation is only a basic safety filter; it is not a security sandbox and does not prove accessibility.

## Integration contract

Pass one issue at a time. The module accepts common axe-core fields such as `id`, `description`, `help`, `impact`, `tags` or `wcag`, `nodes`, `html`, and `selector`. The helper also accepts `purpose` as optional context. If the scanner returns `nodes`, the first three nodes are summarised before sending to the model.

## GitHub contribution

Create/use branch `feature/ai-copilot`, add these files to the shared repository, then:

```bash
git add ai_helper.py remediation.py test_ai.py examples tests .env.example .gitignore requirements.txt README_PERSON2.md
git commit -m "Add Gemini accessibility co-pilot module"
git push -u origin feature/ai-copilot
```

Open a Pull Request into the team's main branch. If the main repository already has `requirements.txt` or `.gitignore`, merge the entries rather than overwriting the team's versions.
