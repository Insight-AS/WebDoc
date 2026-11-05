PROFILE_RULES = {
    "blind": [
        "button-name",
        "image-alt",
        "link-name",
    ],
    "low_vision": [
        "color-contrast",
        "color-contrast-enhanced",
    ],
    "keyboard": [
        "keyboard",
        "tabindex",
    ],
    "cognitive": [
        "heading-order",
        "label",
    ],
}


def map_violations_to_profiles(violations):
    profile_issues = {}

    for profile, rules in PROFILE_RULES.items():
        matched_issues = []

        for violation in violations:
            if violation["id"] in rules:
                matched_issues.append(violation["id"])

        profile_issues[profile] = {
            "issues": matched_issues,
            "total_issues": len(matched_issues),
        }

    return profile_issues

if __name__ == "__main__":
    sample_violations = [
        {"id": "button-name"},
        {"id": "image-alt"},
        {"id": "color-contrast"},
        {"id": "heading-order"},
    ]

    result = map_violations_to_profiles(sample_violations)
    print(result)