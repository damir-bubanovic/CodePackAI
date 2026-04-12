from pathlib import Path


def normalize_path(path: Path) -> str:
    return path.as_posix()


def matches_rule(file_path: Path, rule_target_type: str, pattern: str, base_folder: Path) -> bool:
    relative_path = file_path.relative_to(base_folder)
    relative_path_str = normalize_path(relative_path)

    if rule_target_type == "extension":
        return file_path.suffix.lower() == pattern.lower()

    if rule_target_type == "filename":
        return file_path.name.lower() == pattern.lower()

    if rule_target_type == "folder_name":
        return pattern.lower() in [part.lower() for part in relative_path.parts[:-1]]

    if rule_target_type == "path_contains":
        return pattern.lower() in relative_path_str.lower()

    return False


def should_skip_directory(dir_path: Path, base_folder: Path, rules: list[tuple]) -> bool:
    relative_path = dir_path.relative_to(base_folder)
    folder_parts = [part.lower() for part in relative_path.parts]

    for rule in rules:
        rule_type, target_type, pattern, enabled, priority, notes = rule

        if not enabled:
            continue

        if rule_type != "exclude":
            continue

        if target_type != "folder_name":
            continue

        if pattern.lower() in folder_parts:
            return True

    return False


def classify_file(file_path: Path, base_folder: Path, rules: list[tuple]) -> tuple[str, str | None]:
    """
    Returns:
        (classification, matched_pattern)

    classification can be:
        include, exclude, review, unmatched
    """

    for rule in rules:
        rule_type, target_type, pattern, enabled, priority, notes = rule

        if not enabled:
            continue

        if matches_rule(file_path, target_type, pattern, base_folder):
            if rule_type in {"always_keep", "include", "exclude", "review"}:
                return rule_type, pattern

    return "unmatched", None


def scan_project(project_folder: str, rules: list[tuple]) -> list[dict]:
    base_folder = Path(project_folder).resolve()
    results = []

    for current_root, dirnames, filenames in base_folder.walk():
        current_root_path = Path(current_root)

        dirnames[:] = [
            dirname for dirname in dirnames
            if not should_skip_directory(current_root_path / dirname, base_folder, rules)
        ]

        for filename in filenames:
            file_path = current_root_path / filename
            classification, matched_pattern = classify_file(file_path, base_folder, rules)

            results.append({
                "relative_path": file_path.relative_to(base_folder).as_posix(),
                "size_bytes": file_path.stat().st_size,
                "classification": classification,
                "matched_pattern": matched_pattern,
            })

    return results


def summarize_results(results: list[dict]) -> dict:
    summary = {
        "include": {"count": 0, "size_bytes": 0},
        "exclude": {"count": 0, "size_bytes": 0},
        "review": {"count": 0, "size_bytes": 0},
        "always_keep": {"count": 0, "size_bytes": 0},
        "unmatched": {"count": 0, "size_bytes": 0},
    }

    for item in results:
        classification = item["classification"]

        if classification not in summary:
            continue

        summary[classification]["count"] += 1
        summary[classification]["size_bytes"] += item["size_bytes"]

    return summary