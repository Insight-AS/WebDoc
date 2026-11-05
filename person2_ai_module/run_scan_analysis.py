
import json
from pathlib import Path

from dotenv import load_dotenv

MODULE_DIR = Path(__file__).resolve().parent
load_dotenv(MODULE_DIR / ".env", override=True)

from ai_helper import analyze_issue
from remediation import build_patch_package

INPUT_FILE = MODULE_DIR / "examples" / "backend_results.json"
OUTPUT_FILE = MODULE_DIR / "data" / "ai_analysis_results.json"


def adapt_backend_violation(violation):
    """Convert scanner output into AI-compatible input."""

    raw_nodes = violation.get("nodes") or []
    adapted_nodes = []

    for node in raw_nodes[:3]:
        target = node.get("target") or []

        adapted_nodes.append({
            "html": node.get("html", ""),
            "target": target,
            "failureSummary": (
                node.get("failure_summary")
                or node.get("failureSummary")
                or ""
            )
        })

    first_node = adapted_nodes[0] if adapted_nodes else {}

    target = first_node.get("target", [])

    selector = (
        " | ".join(str(item) for item in target)
        if isinstance(target, list)
        else str(target)
    )

    return {
        **violation,
        "html": violation.get("html") or first_node.get("html", ""),
        "selector": violation.get("selector") or selector,
        "nodes": adapted_nodes,
        "wcag": violation.get("tags") or violation.get("wcag") or []
    }


def analyze_scan_results(results_json, language="English", limit=1):
    """Analyse scanner violations and prepare remediation packages."""

    violations = results_json.get("violations", [])

    if not isinstance(violations, list):
        raise ValueError("Scanner violations must be a list.")

    output = []

    for violation in violations[:limit]:

        issue = adapt_backend_violation(violation)

        print(f"Analyzing: {issue.get('id')}", flush=True)

        try:
            analysis = analyze_issue(issue, language=language)
            analysis_data = analysis.model_dump()

            # Never accept a WCAG reference not supplied by the scanner.
            source_wcag = issue.get("wcag") or issue.get("tags") or []

            if not source_wcag:
                analysis_data["wcag_reference"] = None

            patch = build_patch_package(issue, analysis_data)

            # Page-level structural issues need full-page context.
            page_level_issue = (
                issue.get("id") == "landmark-one-main"
            )

            patch["patch_applicable"] = not page_level_issue

            if page_level_issue:
                patch["verification_status"] = "requires_page_context"
                patch["review_note"] = (
                    "Wrap the primary page content inside a main element. "
                    "Do not replace the html element with a main fragment."
                )

            output.append({
                "issue_id": issue.get("id"),
                "status": "analysis_generated",
                "analysis": analysis_data,
                "patch": patch
            })

            print("AI analysis successful!", flush=True)

        except Exception as error:

            output.append({
                "issue_id": issue.get("id"),
                "status": "failed",
                "error_type": type(error).__name__,
                "error": str(error)[:1000]
            })

            print(
                f"AI analysis failed: {type(error).__name__}",
                flush=True
            )

    return {
        "source_url": (
            results_json.get("final_url")
            or results_json.get("url")
        ),
        "scan_status": results_json.get("scan_status"),
        "total_violations": len(violations),
        "processed_violations": len(output),
        "results": output
    }


if __name__ == "__main__":

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Backend JSON not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8-sig") as file:
        scanner_data = json.load(file)

    print("Backend scanner JSON loaded!", flush=True)

    result = analyze_scan_results(
        scanner_data,
        language="English",
        limit=1
    )

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nIntegration process finished.", flush=True)
    print("Output:", OUTPUT_FILE)
    print("Processed issues:", result["processed_violations"])
