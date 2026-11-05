"""Safety checks and packaging for AI-generated HTML patches.

This module deliberately does not execute code or modify a live website.
A patch remains unverified until the scanner re-tests the preview.
"""

from __future__ import annotations

import re
from html.parser import HTMLParser
from typing import Any, Mapping


FORBIDDEN_TAGS = {"script", "iframe", "object", "embed", "base"}
FORBIDDEN_URL_PREFIXES = ("javascript:", "vbscript:", "data:text/html")


class _FragmentSafetyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.problems: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag_name = tag.lower()
        if tag_name in FORBIDDEN_TAGS:
            self.problems.append(f"Forbidden tag detected: <{tag_name}>")
        for name, value in attrs:
            attr_name = name.lower()
            attr_value = (value or "").strip().lower()
            if attr_name.startswith("on"):
                self.problems.append(f"Inline event handler is not allowed: {attr_name}")
            if attr_name in {"href", "src", "action", "formaction", "xlink:href"}:
                if any(attr_value.startswith(prefix) for prefix in FORBIDDEN_URL_PREFIXES):
                    self.problems.append(f"Unsafe URL value in attribute: {attr_name}")



def validate_html_patch(original_html: str, corrected_html: str) -> dict[str, Any]:
    """Perform basic static safety checks on a proposed HTML fragment.

    Passing these checks does NOT prove that the patch is safe or accessible.
    It only blocks a small set of high-risk HTML patterns before previewing.
    """
    if not isinstance(corrected_html, str) or not corrected_html.strip():
        return {
            "valid": False,
            "problems": ["The generated HTML patch is empty."],
            "warnings": ["Do not apply an empty patch."],
        }

    parser = _FragmentSafetyParser()
    try:
        parser.feed(corrected_html)
        parser.close()
    except Exception as exc:
        parser.problems.append(f"HTML parsing failed: {exc}")

    if re.search(r"<\s*style\b[^>]*>.*?@import|expression\s*\(", corrected_html, re.I | re.S):
        parser.problems.append("Potentially unsafe CSS construct detected.")

    warnings = [
        "Static checks are not a security sandbox.",
        "Do not execute generated JavaScript or apply patches directly to the live website.",
        "Review the patch, preview it in an isolated environment, then re-run axe-core and manual tests.",
    ]
    if original_html.strip() == corrected_html.strip():
        warnings.append("The proposed fragment is identical to the original fragment.")

    return {
        "valid": len(parser.problems) == 0,
        "problems": parser.problems,
        "warnings": warnings,
    }


def build_patch_package(
    issue: Mapping[str, Any], analysis: Mapping[str, Any]
) -> dict[str, Any]:
    """Combine one AI analysis with static checks into a hand-off object.

    The caller should store this object and arrange a temporary, sandboxed preview.
    After a re-scan, update verification_status based on actual scanner results.
    """
    original_html = str(issue.get("html") or "")
    corrected_html = str(analysis.get("corrected_code") or "")
    validation = validate_html_patch(original_html, corrected_html)

    return {
        "issue_id": issue.get("id"),
        "original_code": original_html,
        "corrected_code": corrected_html,
        "recommended_fix": analysis.get("recommended_fix", ""),
        "validation": validation,
        "verification_status": "pending_rescan" if validation["valid"] else "rejected",
        "human_review_required": True,
    }
