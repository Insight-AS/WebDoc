
from playwright.sync_api import sync_playwright
import json
import os
from datetime import datetime


def test_keyboard_navigation(url):

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

        page.locator("body").click(position={"x": 5, "y": 5})

        focused_elements = []

        # Forward navigation
        for i in range(30):

            page.keyboard.press("Tab")

            element = page.evaluate("""
                () => {
                    const el = document.activeElement;

                    return {
                        tag: el.tagName,
                        id: el.id,
                        text: (el.innerText || el.value || "").trim(),
                        aria_label: el.getAttribute("aria-label"),
                        href: el.getAttribute("href"),
                        focus_visible: el.matches(":focus-visible")
                    };
                }
            """)

            if element["tag"] == "BODY":
                break

            focused_elements.append(element)

        # Reverse navigation
        page.keyboard.press("Shift+Tab")

        reverse_element = page.evaluate("""
            () => {
                const el = document.activeElement;

                return {
                    tag: el.tagName,
                    text: (el.innerText || el.value || "").trim(),
                    focus_visible: el.matches(":focus-visible")
                };
            }
        """)

        # Save JSON
        os.makedirs("data", exist_ok=True)

        result = {
            "url": url,
            "timestamp": datetime.now().isoformat(),
            "total_focused_elements": len(focused_elements),
            "focused_elements": focused_elements,
            "reverse_navigation": reverse_element
        }

        with open("data/keyboard_results.json", "w", encoding="utf-8") as file:
            json.dump(result, file, indent=4)

        print("\nKeyboard Test Completed!")
        print("Forward Focused Elements:", len(focused_elements))
        print("Reverse Navigation:", reverse_element)

        browser.close()


if __name__ == "__main__":

    url = input("Enter website URL: ")
    test_keyboard_navigation(url)
