def match_rule(rule, file_path: str, file_name: str):
    rule_type, target_type, pattern, enabled, priority, notes = rule

    if not enabled:
        return False

    pattern = pattern.lower()
    file_path = file_path.lower()
    file_name = file_name.lower()

    if target_type == "extension":
        return file_name.endswith(pattern)

    if target_type == "filename":
        return file_name == pattern

    if target_type == "folder_name":
        return pattern in file_path.split("/")

    if target_type == "path_contains":
        return pattern in file_path

    return False


def classify_file(file_path, file_name, rules):
    matched = []

    for rule in rules:
        if match_rule(rule, file_path, file_name):
            matched.append(rule)

    if not matched:
        return "exclude"

    # priority sort
    matched.sort(key=lambda r: r[4])  # priority

    return matched[0][0]  # rule_type