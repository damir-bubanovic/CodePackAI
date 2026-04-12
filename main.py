from pathlib import Path

from database import initialize_database
from seed_data import seed_profiles, seed_rules
from profile_service import get_rules_for_profile
from scanner import scan_project, summarize_results
from packer import create_zip_from_results


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

    print("\n=== SUMMARY ===")
    for classification, data in summary.items():
        print(
            f"{classification:10} | "
            f"files: {data['count']:5} | "
            f"size: {data['size_bytes']:10} bytes"
        )

    create_zip = input("\nCreate zip with included files only? (y/n): ").strip().lower()
    if create_zip != "y":
        print("Zip creation skipped.")
        return

    project_path = Path(project_folder).resolve()
    zip_name = f"{project_path.name}_{profile_name}.zip"
    output_zip_path = str(project_path.parent / zip_name)

    files_added, total_bytes = create_zip_from_results(
        project_folder=project_folder,
        results=results,
        output_zip_path=output_zip_path,
        allowed_classifications={"include"},
    )

    print("\n=== ZIP CREATED ===")
    print(f"Output: {output_zip_path}")
    print(f"Files added: {files_added}")
    print(f"Total uncompressed bytes packed: {total_bytes}")


if __name__ == "__main__":
    main()