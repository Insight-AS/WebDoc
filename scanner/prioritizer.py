
import json
import os


# Priority mapping
PRIORITY_MAP = {
    "critical": "P1",
    "serious": "P2",
    "moderate": "P3",
    "minor": "P4"
}


def prioritize_issues(input_file="data/results.json"):

    # Read scanner results
    with open(input_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    violations = data.get("violations", [])

    prioritized_issues = []

    # Process every violation
    for issue in violations:

        impact = (issue.get("impact") or "minor").lower()

        priority = PRIORITY_MAP.get(impact, "P4")

        prioritized_issues.append({
            "id": issue.get("id"),
            "impact": impact,
            "priority": priority,
            "description": issue.get("description"),
            "help": issue.get("help"),
            "help_url": issue.get("help_url"),
            "affected_nodes": issue.get("affected_nodes", 0),
            "nodes": issue.get("nodes", [])
        })

    # Sort issues: P1 first, then P2, P3 and P4
    priority_order = {
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4
    }

    prioritized_issues.sort(
        key=lambda issue: priority_order[issue["priority"]]
    )

    # Summary
    summary = {
        "P1": 0,
        "P2": 0,
        "P3": 0,
        "P4": 0
    }

    for issue in prioritized_issues:
        summary[issue["priority"]] += 1

    # Final output
    result = {
        "total_issues": len(prioritized_issues),
        "priority_summary": summary,
        "prioritized_issues": prioritized_issues
    }

    os.makedirs("data", exist_ok=True)

    with open(
        "data/prioritized_results.json",
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(result, file, indent=4)

    print("\nPrioritization Completed!")
    print("Total Issues:", len(prioritized_issues))
    print("Priority Summary:", summary)

    for issue in prioritized_issues:
        print(
            issue["priority"],
            "|",
            issue["impact"],
            "|",
            issue["id"]
        )


if __name__ == "__main__":
    prioritize_issues()
