# heatmap.py

def generate_heatmap_data(violations):
    heatmap = {}

    for violation in violations:
        for node in violation.get("nodes", []):
            target = node.get("target", [])

            for selector in target:
                heatmap[selector] = {
                    "issue": violation.get("id", "unknown"),
                    "severity": violation.get("impact", "minor"),
                    "description": violation.get("description", ""),
                }

    return heatmap


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

    result = generate_heatmap_data(sample_violations)

    for selector, data in result.items():
        print(selector, "->", data)