from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os


def capture_page_context(page):
    """
    Capture a limited structural snapshot of the page.

    Website content is untrusted input. This snapshot is provided
    to Gemini only as context, never as executable instructions.
    """

    return page.evaluate("""
        () => {
            const body = document.body;

            const bodyChildren = Array.from(body.children)
                .filter(element =>
                    !["SCRIPT", "STYLE", "NOSCRIPT"].includes(element.tagName)
                )
                .slice(0, 12)
                .map(element => {
                    const clone = element.cloneNode(true);

                    clone.querySelectorAll(
                        "script, style, noscript"
                    ).forEach(node => node.remove());

                    const allElements = [
                        clone,
                        ...clone.querySelectorAll("*")
                    ];

                    allElements.forEach(node => {
                        Array.from(node.attributes || []).forEach(attr => {
                            if (attr.name.toLowerCase().startsWith("on")) {
                                node.removeAttribute(attr.name);
                            }
                        });
                    });

                    const html = clone.outerHTML;

                    return {
                        tag: element.tagName.toLowerCase(),
                        id: element.id || null,
                        role: element.getAttribute("role"),
                        html: html.slice(0, 1500),
                        truncated: html.length > 1500
                    };
                });

            const landmarks = Array.from(
                document.querySelectorAll(
                    "main, [role='main'], header, nav, footer, aside, [role='region']"
                )
            )
            .slice(0, 30)
            .map(element => ({
                tag: element.tagName.toLowerCase(),
                role: element.getAttribute("role"),
                id: element.id || null,
                aria_label: element.getAttribute("aria-label")
            }));

            const headings = Array.from(
                document.querySelectorAll("h1, h2, h3")
            )
            .slice(0, 20)
            .map(element => ({
                level: element.tagName.toLowerCase(),
                text: (element.innerText || "").slice(0, 150)
            }));

            return {
                title: document.title,
                url: location.href,
                body_children: bodyChildren,
                existing_landmarks: landmarks,
                headings: headings
            };
        }
    """)


def scan_website(url):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="chrome"
        )

        try:
            page = browser.new_page()

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            title = page.title()
            final_url = page.url

            # Capture page structure for context-aware AI analysis.
            page_context = capture_page_context(page)

            # Inject axe-core.
            page.add_script_tag(
                path="node_modules/axe-core/axe.min.js"
            )

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
                    "affected_nodes": len(nodes),
                    "nodes": nodes
                })

            os.makedirs("data", exist_ok=True)

            page.screenshot(
                path="data/website_screenshot.png",
                full_page=True
            )

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
                "page_context": page_context,
                "profiles": {},
                "screenshot": "data/website_screenshot.png"
            }

            with open("data/results.json", "w", encoding="utf-8") as file:
                json.dump(result, file, indent=4, ensure_ascii=False)

            print("\nAccessibility Scan Completed!")
            print("Website:", final_url)
            print("Title:", title)
            print("Total Violations:", len(violations))
            print("Affected Nodes:", total_affected_nodes)
            print("Page context captured:", bool(page_context))
            print("Passed Rules:", len(axe_results["passes"]))
            print("Incomplete Rules:", len(axe_results["incomplete"]))

        finally:
            browser.close()


if __name__ == "__main__":

    website_url = input("Enter website URL: ").strip()

    if website_url.startswith(("http://", "https://")):
        scan_website(website_url)
    else:
        print("Please enter a valid HTTP/HTTPS website URL.")