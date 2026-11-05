import unittest

from remediation import build_patch_package, validate_html_patch


class RemediationValidationTests(unittest.TestCase):
    def test_accepts_simple_accessible_button_fragment(self):
        result = validate_html_patch(
            "<button></button>",
            "<button aria-label='Open shopping cart'>Cart</button>",
        )
        self.assertTrue(result["valid"])

    def test_rejects_script_tag(self):
        result = validate_html_patch("<button></button>", "<script>alert(1)</script>")
        self.assertFalse(result["valid"])

    def test_rejects_inline_event_handler(self):
        result = validate_html_patch("<button></button>", "<button onclick='alert(1)'>Cart</button>")
        self.assertFalse(result["valid"])

    def test_patch_package_stays_pending_until_rescan(self):
        issue = {"id": "button-name", "html": "<button></button>"}
        analysis = {
            "corrected_code": "<button aria-label='Open cart'>Cart</button>",
            "recommended_fix": "Give the button an accessible name.",
        }
        package = build_patch_package(issue, analysis)
        self.assertEqual(package["verification_status"], "pending_rescan")
        self.assertTrue(package["human_review_required"])


if __name__ == "__main__":
    unittest.main()
