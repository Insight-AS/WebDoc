from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    print("Launching Google Chrome...")

    browser = p.chromium.launch(
        headless=False,
        channel="chrome"
    )

    page = browser.new_page()

    page.goto("https://example.com")

    print("Website Title:", page.title())
    print("Website URL:", page.url)

    browser.close()

    print("Browser test successful!")