
import json
import time
from pathlib import Path
from collections.abc import Mapping

from dotenv import load_dotenv

# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

MODULE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = MODULE_DIR.parent

# Load Gemini API configuration.
load_dotenv(MODULE_DIR / ".env", override=True)

from ai_helper import analyze_issue  # noqa: E402
from remediation import build_patch_package  # noqa: E402

# Actual backend scanner output.
INPUT_FILE = PROJECT_DIR / "data" / "results.json"

# Generated AI analysis output.
OUTPUT_FILE = MODULE_DIR / "data" / "ai_analysis_results.json"


# --------------------------------------------------
# RETRY CONFIGURATION
# --------------------------------------------------

MAX_RETRY_ATTEMPTS = 3
BASE_RETRY_DELAY = 2
MAX_RETRY_DELAY = 8

RETRYABLE_ERROR_MARKERS = (
    "429",
    "500",
    "502",
    "503",
    "504",
    "UNAVAILABLE",
    "RESOURCE_EXHAUSTED",
    "DEADLINE_EXCEEDED",
    "TIMEOUT",
    "TIMED OUT",
    "CONNECTION RESET",
    "SERVICE UNAVAILABLE",
    # Retry transient or truncated structured responses as well.
    "INVALID JSON",
    "EOF WHILE PARSING",
)


# --------------------------------------------------
# BACKEND JSON ADAPTER
# --------------------------------------------------

def adapt_backend_violation(violation, page_context=None):
    """Convert a backend scanner violation into the AI module format."""

    if not isinstance(violation, Mapping):
        raise TypeError("Each violation must be a dictionary.")

    raw_nodes = violation.get("nodes") or []
    if not isinstance(raw_nodes, list):
        raw_nodes = []

    adapted_nodes = []

    # Preserve up to 15 affected nodes for context-aware analysis.
    for node in raw_nodes[:15]:
        if not isinstance(node, Mapping):
            continue

        target = node.get("target") or []
        if isinstance(target, str):
            target = [target]

        adapted_nodes.append({
            "html": node.get("html", ""),
            "target": target,
            "failureSummary": (
                node.get("failure_summary")
                or node.get("failureSummary")
                or ""
            ),
        })

    first_node = adapted_nodes[0] if adapted_nodes else {}
    target = first_node.get("target", [])

    selector = (
        " | ".join(str(item) for item in target)
        if isinstance(target, list)
        else str(target)
    )

    # Preserve original axe-core tags.
    source_tags = (
        violation.get("tags")
        or violation.get("wcag")
        or []
    )
    if isinstance(source_tags, str):
        source_tags = [source_tags]

    return {
        **violation,
        "html": (
            violation.get("html")
            or first_node.get("html", "")
        ),
        "selector": (
            violation.get("selector")
            or selector
        ),
        "nodes": adapted_nodes,
        "page_context": page_context or {},
        "wcag": source_tags,
    }


# --------------------------------------------------
# GEMINI AUTOMATIC RETRY
# --------------------------------------------------

def analyze_issue_with_retry(
    issue,
    language="English",
    max_attempts=MAX_RETRY_ATTEMPTS,
):
    """Retry temporary Gemini failures and incomplete JSON responses.

    Maximum attempts include the first request. Only errors whose messages
    match RETRYABLE_ERROR_MARKERS are retried.
    """

    if max_attempts < 1:
        raise ValueError("max_attempts must be at least 1.")

    for attempt in range(1, max_attempts + 1):
        try:
            return analyze_issue(
                issue,
                language=language,
            )

        except Exception as error:
            error_message = str(error).upper()

            temporary_error = any(
                marker in error_message
                for marker in RETRYABLE_ERROR_MARKERS
            )

            # Do not retry permanent errors.
            if not temporary_error:
                raise

            # No attempts remaining.
            if attempt == max_attempts:
                print(
                    f"Gemini retry limit reached ({max_attempts} attempts).",
                    flush=True,
                )
                raise

            delay = min(
                MAX_RETRY_DELAY,
                BASE_RETRY_DELAY * (2 ** (attempt - 1)),
            )

            print(
                f"Temporary Gemini error: {error_message[:180]}",
                flush=True,
            )
            print(
                f"Retrying attempt {attempt + 1}/{max_attempts} "
                f"in {delay} seconds...",
                flush=True,
            )

            time.sleep(delay)

    raise RuntimeError("Gemini analysis failed unexpectedly.")


# --------------------------------------------------
# AI ANALYSIS PIPELINE
# --------------------------------------------------

def analyze_scan_results(
    results_json,
    language="English",
    limit=None,
):
    """Analyse scanner violations and generate explanations and patches.

    limit=None processes all violations.
    """

    if not isinstance(results_json, Mapping):
        raise ValueError("Scanner JSON must be an object.")

    violations = results_json.get("violations", [])
    if not isinstance(violations, list):
        raise ValueError("Scanner violations must be a list.")

    if limit is not None:
        if (
            not isinstance(limit, int)
            or isinstance(limit, bool)
            or limit < 0
        ):
            raise ValueError("limit must be None or a non-negative integer.")

    selected_violations = (
        violations if limit is None else violations[:limit]
    )

    output = []
    successful_count = 0
    failed_count = 0

    print(
        f"Total scanner violations: {len(violations)}",
        flush=True,
    )
    print(
        f"Violations selected for AI: {len(selected_violations)}",
        flush=True,
    )

    # --------------------------------------------------
    # PROCESS EACH VIOLATION
    # --------------------------------------------------

    for index, violation in enumerate(selected_violations, start=1):
        issue_id = (
            violation.get("id", "unknown")
            if isinstance(violation, Mapping)
            else "unknown"
        )

        print(
            f"\n[{index}/{len(selected_violations)}] Analyzing: {issue_id}",
            flush=True,
        )

        try:
            # Pass the full bounded page snapshot alongside the violation.
            issue = adapt_backend_violation(
                violation,
                page_context=results_json.get("page_context", {}),
            )

            analysis = analyze_issue_with_retry(
                issue,
                language=language,
                max_attempts=MAX_RETRY_ATTEMPTS,
            )

            analysis_data = analysis.model_dump()

            # Never invent a WCAG reference when the scanner did not provide tags.
            source_wcag = (
                issue.get("wcag")
                or issue.get("tags")
                or []
            )
            if not source_wcag:
                analysis_data["wcag_reference"] = None

            patch = build_patch_package(
                issue,
                analysis_data,
            )

            # Page-level main landmark issue needs page context and manual review.
            page_level_issue = issue.get("id") == "landmark-one-main"
            patch["patch_applicable"] = not page_level_issue

            if page_level_issue:
                patch["verification_status"] = "requires_page_context"
                patch["review_note"] = (
                    "Review the complete page structure and existing landmarks. "
                    "Place primary page content inside one appropriate main landmark. "
                    "Do not replace the html element with a main fragment."
                )

            output.append({
                "issue_id": issue_id,
                "status": "analysis_generated",
                "analysis": analysis_data,
                "patch": patch,
            })

            successful_count += 1
            print(
                f"AI analysis successful: {issue_id}",
                flush=True,
            )

        except Exception as error:
            # One failed issue should not stop other issues.
            output.append({
                "issue_id": issue_id,
                "status": "failed",
                "error_type": type(error).__name__,
                "error": str(error)[:1000],
            })

            failed_count += 1
            print(
                f"AI analysis failed: {issue_id} - "
                f"{type(error).__name__}: {error}",
                flush=True,
            )

    return {
        "source_url": (
            results_json.get("final_url")
            or results_json.get("url")
        ),
        "scan_status": results_json.get("scan_status"),
        "total_violations": len(violations),
        "processed_violations": len(output),
        "successful_analyses": successful_count,
        "failed_analyses": failed_count,
        "results": output,
    }


# --------------------------------------------------
# MAIN EXECUTION
# --------------------------------------------------

if __name__ == "__main__":
    print("\n====================================")
    print("       WEBDOC AI ACCESSIBILITY")
    print("====================================\n")

    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Backend JSON not found: {INPUT_FILE}"
        )

    with INPUT_FILE.open("r", encoding="utf-8-sig") as file:
        scanner_data = json.load(file)

    print("Backend scanner JSON loaded!")
    print(
        "Website:",
        scanner_data.get("final_url") or scanner_data.get("url"),
    )

    result = analyze_scan_results(
        scanner_data,
        language="English",
        limit=None,
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            indent=4,
            ensure_ascii=False,
        )

    print("\n====================================")
    print("       ANALYSIS COMPLETED")
    print("====================================")
    print("Total violations:", result["total_violations"])
    print("Processed violations:", result["processed_violations"])
    print("Successful analyses:", result["successful_analyses"])
    print("Failed analyses:", result["failed_analyses"])
    print("\nOutput saved at:")
    print(OUTPUT_FILE)
    print("\n====================================")