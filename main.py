from database import initialize_database
from seed_data import seed_profiles, seed_rules
from profile_service import get_rules_for_profile
from scanner import scan_project, summarize_results


def main() -> None:
    initialize_database()
    seed_profiles()
    seed_rules()

    project_folder = input("Enter project folder path: ").strip()
    profile_name = input("Enter profile name (example: Python, Unity, CSharp_DotNet): ").strip()

    rules = get_rules_for_profile(profile_name)

    if not rules:
        print(f"No rules found for profile: {profile_name}")
        return

    results = scan_project(project_folder, rules)
    summary = summarize_results(results)

    print("\n=== SCAN RESULTS ===")
    for item in results[:50]:
        print(
            f"{item['classification']:10} | "
            f"{item['size_bytes']:8} bytes | "
            f"{item['relative_path']}"
        )

    print("\n=== SUMMARY ===")
    for classification, data in summary.items():
        print(
            f"{classification:10} | "
            f"files: {data['count']:5} | "
            f"size: {data['size_bytes']:10} bytes"
        )

    unmatched = [item for item in results if item["classification"] == "unmatched"]
    review = [item for item in results if item["classification"] == "review"]

    print("\n=== FIRST 30 UNMATCHED FILES ===")
    for item in unmatched[:30]:
        print(
            f"{item['size_bytes']:8} bytes | "
            f"{item['relative_path']}"
        )

    print("\n=== FIRST 30 REVIEW FILES ===")
    for item in review[:30]:
        print(
            f"{item['size_bytes']:8} bytes | "
            f"{item['relative_path']}"
        )

    print(f"\nTotal files scanned: {len(results)}")


if __name__ == "__main__":
    main()