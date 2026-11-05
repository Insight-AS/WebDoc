
from playwright.sync_api import sync_playwright
from datetime import datetime
import json
import os


def test_user_journey(url):

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=False,
            channel="chrome"
        )

        page = browser.new_page()

        results = []

        # Step 1: Open homepage
        try:
            response = page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=60000
            )

            results.append({
                "step": "Open homepage",
                "status": "passed" if response and response.ok else "failed",
                "url": page.url
            })

        except Exception as e:
            results.append({
                "step": "Open homepage",
                "status": "failed",
                "error": str(e)
            })

        # Step 2: Check navigation links
        if page.url != "about:blank":

            links = page.locator("a[href]")
            total_links = min(links.count(), 10)

            for i in range(total_links):

                link = links.nth(i)

                try:
                    href = link.get_attribute("href")
                    text = link.inner_text().strip()

                    results.append({
                        "step": "Check navigation link",
                        "link_text": text,
                        "href": href,
                        "status": "found"
                    })

                except Exception as e:
                    results.append({
                        "step": "Check navigation link",
                        "status": "failed",
                        "error": str(e)
                    })

        # Step 3: Check buttons
        buttons = page.locator("button")
        button_count = buttons.count()

        results.append({
            "step": "Check buttons",
            "status": "passed",
            "total_buttons": button_count
        })

        # Step 4: Check forms
        forms = page.locator("form")
        form_count = forms.count()

        results.append({
            "step": "Check forms",
            "status": "passed",
            "total_forms": form_count
        })

        # Step 5: Check page title
        title = page.title()

        results.append({
            "step": "Check page title",
            "status": "passed" if title else "failed",
            "title": title
        })

        # Save results
        os.makedirs("data", exist_ok=True)

        report = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "total_steps": len(results),
            "results": results
        }

        with open(
            "data/journey_results.json",
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(report, file, indent=4)

        print("\nUser Journey Test Completed!")
        print("Total Steps:", len(results))

        for item in results:
            print(item)

        browser.close()


if __name__ == "__main__":

    website_url = input("Enter website URL: ")

    test_user_journey(website_url)

