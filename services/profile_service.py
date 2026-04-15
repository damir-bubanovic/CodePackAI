from database.profile_repository import (
    fetch_all_profiles,
    fetch_profile_by_name,
    fetch_profile_by_id,
    insert_profile,
    update_profile_record,
    delete_profile_record,
    duplicate_profile_record,
)
from database.rule_repository import (
    fetch_rules_for_profile,
    fetch_rules_for_profile_id,
    insert_rule,
    update_rule_record,
    delete_rule_record,
    delete_rules_for_profile_record,
    insert_rules_bulk,
    insert_rule_copies,
)


def get_all_profiles():
    return fetch_all_profiles()


def get_profile_by_name(profile_name: str):
    return fetch_profile_by_name(profile_name)


def get_profile_by_id(profile_id: int):
    return fetch_profile_by_id(profile_id)


def get_rules_for_profile(profile_name: str):
    return fetch_rules_for_profile(profile_name)


def get_rules_for_profile_id(profile_id: int):
    return fetch_rules_for_profile_id(profile_id)


def create_profile(name: str, description: str = "", is_builtin: int = 0) -> int:
    return insert_profile(name=name, description=description, is_builtin=is_builtin)


def update_profile(profile_id: int, name: str, description: str) -> None:
    update_profile_record(profile_id=profile_id, name=name, description=description)


def delete_profile(profile_id: int) -> bool:
    return delete_profile_record(profile_id)


def create_rule(
    profile_id: int,
    rule_type: str,
    target_type: str,
    pattern: str,
    enabled: int = 1,
    priority: int = 100,
    notes: str | None = None,
) -> int:
    return insert_rule(
        profile_id=profile_id,
        rule_type=rule_type,
        target_type=target_type,
        pattern=pattern,
        enabled=enabled,
        priority=priority,
        notes=notes,
    )


def update_rule(
    rule_id: int,
    rule_type: str,
    target_type: str,
    pattern: str,
    enabled: int,
    priority: int,
    notes: str | None = None,
) -> None:
    update_rule_record(
        rule_id=rule_id,
        rule_type=rule_type,
        target_type=target_type,
        pattern=pattern,
        enabled=enabled,
        priority=priority,
        notes=notes,
    )


def delete_rule(rule_id: int) -> None:
    delete_rule_record(rule_id)


def duplicate_profile(
    source_profile_id: int,
    new_name: str,
    new_description: str = "",
) -> int | None:
    new_profile_id, source_rules = duplicate_profile_record(
        source_profile_id=source_profile_id,
        new_name=new_name,
        new_description=new_description,
    )

    if new_profile_id is None:
        return None

    insert_rule_copies(new_profile_id, source_rules)
    return new_profile_id


def import_rules_to_profile(
    profile_id: int,
    rules: list[dict],
    replace_existing: bool = False,
) -> int:
    if replace_existing:
        delete_rules_for_profile(profile_id)

    return create_rules_bulk(profile_id, rules)


def delete_rules_for_profile(profile_id: int) -> None:
    delete_rules_for_profile_record(profile_id)


def create_rules_bulk(profile_id: int, rules: list[dict]) -> int:
    return insert_rules_bulk(profile_id, rules)