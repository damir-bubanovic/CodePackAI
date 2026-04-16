from pathlib import Path

from core.file_utils import iter_files, get_relative_path, get_file_size
from core.rule_engine import classify_file


def scan_project(project_folder: str, rules):
    base_path = Path(project_folder)

    results = []

    for file_path in iter_files(project_folder):
        relative_path = get_relative_path(base_path, file_path)
        file_name = file_path.name
        size_bytes = get_file_size(file_path)

        classification = classify_file(
            file_path=relative_path,
            file_name=file_name,
            rules=rules,
        )

        results.append({
            "relative_path": relative_path,
            "size_bytes": size_bytes,
            "classification": classification,
        })

    return results


def summarize_results(results):
    summary = {}

    for item in results:
        cls = item["classification"]
        size = item["size_bytes"]

        if cls not in summary:
            summary[cls] = {"count": 0, "size_bytes": 0}

        summary[cls]["count"] += 1
        summary[cls]["size_bytes"] += size

    return summary