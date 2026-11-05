
from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os


def scan_website(url):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="chrome"
        )

        page = browser.new_page()

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Basic website information
        title = page.title()
        final_url = page.url

        # Inject axe-core into the webpage
        page.add_script_tag(
            path="node_modules/axe-core/axe.min.js"
        )

        # Run accessibility test
        axe_results = page.evaluate("""
            async () => await axe.run(document)
        """)

        violations = []

        impact_counts = {
            "critical": 0,
            "serious": 0,
            "moderate": 0,
            "minor": 0
        }

        total_affected_nodes = 0

        # Extract violation details
        for issue in axe_results["violations"]:

            nodes = []

            for node in issue["nodes"]:

                nodes.append({
                    "html": node["html"],
                    "target": node["target"],
                    "failure_summary": node["failureSummary"]
                })

            impact = issue["impact"] or "minor"

            impact_counts[impact] += 1
            total_affected_nodes += len(nodes)

            violations.append({
                "id": issue["id"],
                "impact": impact,
                "description": issue["description"],
                "help": issue["help"],
                "help_url": issue["helpUrl"],
                "tags": issue.get("tags", []),
                "affected_nodes": len(nodes),
                "nodes": nodes
            })

        # Create data folder
        os.makedirs("data", exist_ok=True)

        # Capture screenshot
        page.screenshot(
            path="data/website_screenshot.png",
            full_page=True
        )

        # Final report
        result = {
            "schema_version": "1.0",
            "url": url,
            "final_url": final_url,
            "page_title": title,
            "timestamp": datetime.now().isoformat(),
            "scan_status": "completed",
            "score": None,

            "summary": {
                "total_violations": len(violations),
                "total_affected_nodes": total_affected_nodes,
                "impact_counts": impact_counts,
                "passes": len(axe_results["passes"]),
                "incomplete": len(axe_results["incomplete"])
            },

            "violations": violations,
            "profiles": {},
            "screenshot": "data/website_screenshot.png"
        }

        # Save JSON report
        with open("data/results.json", "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)

        browser.close()

        print("\nAccessibility Scan Completed!")
        print("Website:", final_url)
        print("Title:", title)
        print("Total Violations:", len(violations))
        print("Affected Nodes:", total_affected_nodes)
        print("Passed Rules:", len(axe_results["passes"]))
        print("Incomplete Rules:", len(axe_results["incomplete"]))


if __name__ == "__main__":

    website_url = input("Enter website URL: ")

    scan_website(website_url)
