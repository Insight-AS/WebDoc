"""Manual smoke test: calls Gemini using examples/sample_issue.json."""

import json
from pathlib import Path

from ai_helper import analyze_issue


if __name__ == "__main__":
    sample_path = Path(__file__).parent / "examples" / "sample_issue.json"
    issue = json.loads(sample_path.read_text(encoding="utf-8"))
    result = analyze_issue(issue, language="English")
    print(result.model_dump_json(indent=2))
