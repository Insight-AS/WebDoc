from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os


# The heatmap in app.py is drawn over the screenshot. To keep the screenshot
# and heatmap coordinates aligned, this scanner captures the initial viewport
# rather than attempting an enormous full-page screenshot.
VIEWPORT_WIDTH = 1280
VIEWPORT_HEIGHT = 900
SCREENSHOT_PATH = os.path.join("data", "website_screenshot.png")
RESULTS_PATH = os.path.join("data", "results.json")
AXE_SCRIPT_PATH = os.path.join("node_modules", "axe-core", "axe.min.js")


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
    """Capture the visible portion of an affected element in viewport CSS pixels.

    Elements outside the initial viewport return None. This keeps heatmap
    markers aligned with the viewport screenshot and avoids placing off-screen
    elements at incorrect positions.
    """

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
                const viewportWidth = window.innerWidth;
                const viewportHeight = window.innerHeight;

                // Ignore zero-sized elements and elements outside the viewport.
                if (
                    rect.width <= 0 ||
                    rect.height <= 0 ||
                    rect.right <= 0 ||
                    rect.bottom <= 0 ||
                    rect.left >= viewportWidth ||
                    rect.top >= viewportHeight
                ) {
                    return null;
                }

                // Clip partially visible elements to the screenshot viewport.
                const left = Math.max(0, rect.left);
                const top = Math.max(0, rect.top);
                const right = Math.min(viewportWidth, rect.right);
                const bottom = Math.min(viewportHeight, rect.bottom);

                return {
                    x: Number(left.toFixed(2)),
                    y: Number(top.toFixed(2)),
                    width: Number((right - left).toFixed(2)),
                    height: Number((bottom - top).toFixed(2)),
                    right: Number(right.toFixed(2)),
                    bottom: Number(bottom.toFixed(2)),
                    tag: element.tagName.toLowerCase(),
                    captured: true
                };
            }
        """, axe_target)

    except Exception:
        return None


def capture_screenshot_metadata(page):
    """Capture screenshot and document dimensions for heatmap scaling."""

    try:
        return page.evaluate("""
            () => {
                const documentWidth = Math.max(
                    document.documentElement.scrollWidth,
                    document.body ? document.body.scrollWidth : 0
                );
                const documentHeight = Math.max(
                    document.documentElement.scrollHeight,
                    document.body ? document.body.scrollHeight : 0
                );

                return {
                    // css_width/css_height describe the actual screenshot.
                    css_width: window.innerWidth,
                    css_height: window.innerHeight,
                    viewport_width: window.innerWidth,
                    viewport_height: window.innerHeight,
                    document_width: documentWidth,
                    document_height: documentHeight,
                    device_pixel_ratio: window.devicePixelRatio || 1,
                    capture_mode: "viewport"
                };
            }
        """)

    except Exception:
        return {
            "css_width": VIEWPORT_WIDTH,
            "css_height": VIEWPORT_HEIGHT,
            "viewport_width": VIEWPORT_WIDTH,
            "viewport_height": VIEWPORT_HEIGHT,
            "capture_mode": "viewport"
        }


def scan_website(url):
    """Run axe-core, save scan JSON, and capture a viewport-sized screenshot."""

    os.makedirs("data", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            channel="chrome"
        )

        try:
            page = browser.new_page(
                viewport={
                    "width": VIEWPORT_WIDTH,
                    "height": VIEWPORT_HEIGHT
                },
                device_scale_factor=1
            )

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            # Keep all measurements relative to the top of the page.
            page.evaluate("window.scrollTo(0, 0)")
            page.wait_for_timeout(300)

            title = page.title()
            final_url = page.url

            # Capture page structure for the AI explanation module.
            page_context = capture_page_context(page)

            # Inject axe-core from the project's local node_modules folder.
            page.add_script_tag(path=AXE_SCRIPT_PATH)

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

                    # The bounding box is captured in the same viewport that
                    # will be saved below. Off-screen elements receive None.
                    bounding_box = capture_element_bounds(page, target)

                    nodes.append({
                        "html": node.get("html", ""),
                        "target": target,
                        "failure_summary": node.get("failureSummary"),
                        "bounding_box": bounding_box,
                        "coordinate_status": (
                            "captured" if bounding_box else "not_found"
                        )
                    })

                impact = issue.get("impact") or "minor"
                impact_counts.setdefault(impact, 0)
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

            # Reset to the top immediately before screenshot capture as well.
            page.evaluate("window.scrollTo(0, 0)")
            screenshot_metadata = capture_screenshot_metadata(page)

            # IMPORTANT: full_page=False prevents Chrome from allocating a
            # gigantic bitmap for very long or infinite-scroll webpages.
            page.screenshot(
                path=SCREENSHOT_PATH,
                full_page=False,
                timeout=30000
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
                "screenshot": SCREENSHOT_PATH.replace("\\", "/"),
                "screenshot_metadata": screenshot_metadata
            }

            with open(RESULTS_PATH, "w", encoding="utf-8") as file:
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
            print("Nodes with heatmap coordinates:", located_nodes)
            print("Page context captured:", bool(page_context))
            print("Passed Rules:", len(axe_results["passes"]))
            print("Incomplete Rules:", len(axe_results["incomplete"]))
            print("Screenshot mode: viewport (", VIEWPORT_WIDTH, "x", VIEWPORT_HEIGHT, ")")
            print("Screenshot saved:", SCREENSHOT_PATH)
            print("Results saved:", RESULTS_PATH)

        finally:
            browser.close()


if __name__ == "__main__":
    website_url = input("Enter website URL: ").strip()

    if website_url.startswith(("http://", "https://")):
        scan_website(website_url)
    else:
        print("Please enter a valid HTTP/HTTPS website URL.")
