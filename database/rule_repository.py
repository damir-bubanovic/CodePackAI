from database import get_connection


def fetch_rules_for_profile(profile_name: str):
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM profiles WHERE name = ?", (profile_name,))
        row = cursor.fetchone()

        if not row:
            return []

        profile_id = row[0]

        cursor.execute("""
            SELECT rule_type, target_type, pattern, enabled, priority, notes
            FROM rules
            WHERE profile_id = ?
            ORDER BY priority ASC, rule_type ASC, pattern ASC
        """, (profile_id,))

        return cursor.fetchall()


def fetch_rules_for_profile_id(profile_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, rule_type, target_type, pattern, enabled, priority, notes
            FROM rules
            WHERE profile_id = ?
            ORDER BY priority ASC, rule_type ASC, pattern ASC
        """, (profile_id,))
        return cursor.fetchall()


def insert_rule(
    profile_id: int,
    rule_type: str,
    target_type: str,
    pattern: str,
    enabled: int = 1,
    priority: int = 100,
    notes: str | None = None,
) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO rules (profile_id, rule_type, target_type, pattern, enabled, priority, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (profile_id, rule_type, target_type, pattern, enabled, priority, notes))
        conn.commit()
        return cursor.lastrowid


def update_rule_record(
    rule_id: int,
    rule_type: str,
    target_type: str,
    pattern: str,
    enabled: int,
    priority: int,
    notes: str | None = None,
) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE rules
            SET rule_type = ?, target_type = ?, pattern = ?, enabled = ?, priority = ?, notes = ?
            WHERE id = ?
        """, (rule_type, target_type, pattern, enabled, priority, notes, rule_id))
        conn.commit()


def delete_rule_record(rule_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        conn.commit()


def delete_rules_for_profile_record(profile_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rules WHERE profile_id = ?", (profile_id,))
        conn.commit()


def insert_rules_bulk(profile_id: int, rules: list[dict]) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()

        rows_to_insert = []
        for rule in rules:
            rows_to_insert.append((
                profile_id,
                rule["rule_type"],
                rule["target_type"],
                rule["pattern"],
                rule.get("enabled", 1),
                rule.get("priority", 100),
                rule.get("notes"),
            ))

        cursor.executemany("""
            INSERT INTO rules (profile_id, rule_type, target_type, pattern, enabled, priority, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, rows_to_insert)

        conn.commit()
        return len(rows_to_insert)


def insert_rule_copies(profile_id: int, rules: list[tuple]) -> None:
    if not rules:
        return

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.executemany("""
            INSERT INTO rules (profile_id, rule_type, target_type, pattern, enabled, priority, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, [
            (profile_id, rule_type, target_type, pattern, enabled, priority, notes)
            for rule_type, target_type, pattern, enabled, priority, notes in rules
        ])

        conn.commit()