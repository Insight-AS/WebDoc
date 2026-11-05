# prioritizer.py

SEVERITY_WEIGHTS = {
    "critical": 4,
    "serious": 3,
    "moderate": 2,
    "minor": 1,
}


def prioritize_issues(violations):
    prioritized = []

    for violation in violations:
        severity = violation.get("impact", "minor")

        score = SEVERITY_WEIGHTS.get(severity, 1)

        prioritized.append({
            "id": violation.get("id", "unknown"),
            "description": violation.get("description", ""),
            "severity": severity,
            "priority_score": score,
        })

    prioritized.sort(
        key=lambda issue: issue["priority_score"],
        reverse=True
    )

    return prioritized


if __name__ == "__main__":
    sample_violations = [
        {
            "id": "image-alt",
            "description": "Image is missing alternative text",
            "impact": "critical",
        },
        {
            "id": "color-contrast",
            "description": "Insufficient color contrast",
            "impact": "serious",
        },
        {
            "id": "heading-order",
            "description": "Heading order is incorrect",
            "impact": "moderate",
        },
    ]

    result = prioritize_issues(sample_violations)

    for issue in result:
        print(issue)