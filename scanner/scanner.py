from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os


def capture_page_context(page):
    """Capture a limited structural snapshot for AI context."""

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


def capture_element_bounds(page, axe_target):
    """Capture affected element coordinates in document CSS pixels."""

    try:
        return page.evaluate("""
            (target) => {
                const path = Array.isArray(target) ? target : [target];

                let scope = document;
                let element = null;

                for (const segment of path) {

                    const candidates = Array.isArray(segment)
                        ? segment : [segment];

                    let match = null;

                    for (const selector of candidates) {

                        if (
                            typeof selector !== "string" ||
                            !selector.trim()
                        ) {
                            continue;
                        }

                        try {
                            match = scope.querySelector(selector);
                        } catch (_) {
                            match = null;
                        }

                        if (match) break;
                    }

                    if (!match) return null;

                    element = match;
                    scope = element.shadowRoot || element;
                }

                if (!element) return null;

                const rect = element.getBoundingClientRect();

                const x = rect.left + window.scrollX;
                const y = rect.top + window.scrollY;

                return {
                    x: Number(x.toFixed(2)),
                    y: Number(y.toFixed(2)),
                    width: Number(rect.width.toFixed(2)),
                    height: Number(rect.height.toFixed(2)),
                    tag: element.tagName.toLowerCase(),
                    captured: true
                };
            }
        """, axe_target)

    except Exception:
        return None


def capture_screenshot_metadata(page):
    """Capture dimensions for screenshot overlay scaling."""

    try:
        return page.evaluate("""
            () => ({
                css_width: Math.max(
                    document.documentElement.scrollWidth,
                    document.body ? document.body.scrollWidth : 0
                ),
                css_height: Math.max(
                    document.documentElement.scrollHeight,
                    document.body ? document.body.scrollHeight : 0
                ),
                viewport_width: window.innerWidth,
                viewport_height: window.innerHeight,
                device_pixel_ratio: window.devicePixelRatio || 1
            })
        """)

    except Exception:
        return {}


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

            # Capture page structure.
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

                    target = node.get("target") or []

                    # Capture actual screen position.
                    bounding_box = capture_element_bounds(
                        page,
                        target
                    )

                    nodes.append({
                        "html": node.get("html", ""),
                        "target": target,
                        "failure_summary": node.get("failureSummary"),
                        "bounding_box": bounding_box,
                        "coordinate_status": (
                            "captured"
                            if bounding_box
                            else "not_found"
                        )
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

            screenshot_metadata = capture_screenshot_metadata(page)

            # Capture full-page screenshot.
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

                "screenshot": "data/website_screenshot.png",
                "screenshot_metadata": screenshot_metadata
            }

            with open(
                "data/results.json",
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    result,
                    file,
                    indent=4,
                    ensure_ascii=False
                )

            located_nodes = sum(
                1
                for issue in violations
                for item in issue.get("nodes", [])
                if item.get("bounding_box")
            )

            print("\nAccessibility Scan Completed!")
            print("Website:", final_url)
            print("Title:", title)
            print("Total Violations:", len(violations))
            print("Affected Nodes:", total_affected_nodes)

            print(
                "Nodes with heatmap coordinates:",
                located_nodes
            )

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