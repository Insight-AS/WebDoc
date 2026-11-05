# features.py

from profiles import map_violations_to_profiles
from prioritizer import prioritize_issues
from heatmap import generate_heatmap_data


def analyze_accessibility(violations):
    profile_results = map_violations_to_profiles(violations)

    prioritized_issues = prioritize_issues(violations)

    heatmap_data = generate_heatmap_data(violations)

    return {
        "profiles": profile_results,
        "prioritized_issues": prioritized_issues,
        "heatmap": heatmap_data,
    }


if __name__ == "__main__":
    sample_violations = [
        {
            "id": "image-alt",
            "impact": "critical",
            "description": "Image missing alt text",
            "nodes": [
                {"target": ["img.hero-image"]},
            ],
        },
        {
            "id": "color-contrast",
            "impact": "serious",
            "description": "Low color contrast",
            "nodes": [
                {"target": ["button.submit-btn"]},
            ],
        },
    ]

    result = analyze_accessibility(sample_violations)

    print("ACCESSIBILITY ANALYSIS")
    print(result)