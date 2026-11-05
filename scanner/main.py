
from scanner.scanner import scan_website
from scanner.keyboard_test import test_keyboard_navigation
from scanner.journey_tester import test_user_journey
from scanner.prioritizer import prioritize_issues


def main():

    print("=" * 45)
    print("       AI WEBSITE ACCESSIBILITY DOCTOR")
    print("=" * 45)

    url = input("\nEnter website URL: ").strip()

    if not url.startswith(("http://", "https://")):
        print("Invalid URL! Please enter a valid HTTP/HTTPS URL.")
        return

    try:

        # Step 1: Accessibility Scan
        print("\n[1/4] Running Accessibility Scanner...")
        scan_website(url)

        # Step 2: Keyboard Test
        print("\n[2/4] Running Keyboard Navigation Test...")
        test_keyboard_navigation(url)

        # Step 3: Journey Test
        print("\n[3/4] Running Journey Tester...")
        test_user_journey(url)

        # Step 4: Prioritization
        print("\n[4/4] Prioritizing Accessibility Issues...")
        prioritize_issues()

        print("\n" + "=" * 45)
        print("       ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 45)

        print("\nGenerated Reports:")
        print("- data/results.json")
        print("- data/keyboard_results.json")
        print("- data/journey_results.json")
        print("- data/prioritized_results.json")
        print("- data/website_screenshot.png")

    except Exception as e:
        print("\nAn error occurred:", e)


if __name__ == "__main__":
    main()
