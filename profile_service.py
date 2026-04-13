from database import get_connection


def get_all_profiles():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, is_builtin
            FROM profiles
            ORDER BY is_builtin DESC, name ASC
        """)
        return cursor.fetchall()


def get_profile_by_name(profile_name: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, is_builtin, created_at, updated_at
            FROM profiles
            WHERE name = ?
        """, (profile_name,))
        return cursor.fetchone()


def get_profile_by_id(profile_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, is_builtin, created_at, updated_at
            FROM profiles
            WHERE id = ?
        """, (profile_id,))
        return cursor.fetchone()


def get_rules_for_profile(profile_name: str):
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


def get_rules_for_profile_id(profile_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, rule_type, target_type, pattern, enabled, priority, notes
            FROM rules
            WHERE profile_id = ?
            ORDER BY priority ASC, rule_type ASC, pattern ASC
        """, (profile_id,))
        return cursor.fetchall()


def create_profile(name: str, description: str = "", is_builtin: int = 0) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO profiles (name, description, is_builtin, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        """, (name, description, is_builtin))
        conn.commit()
        return cursor.lastrowid


def update_profile(profile_id: int, name: str, description: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE profiles
            SET name = ?, description = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (name, description, profile_id))
        conn.commit()


def delete_profile(profile_id: int) -> bool:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT is_builtin FROM profiles WHERE id = ?", (profile_id,))
        row = cursor.fetchone()

        if not row:
            return False

        is_builtin = row[0]
        if is_builtin:
            return False

        cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
        conn.commit()
        return True


def create_rule(
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


def delete_rule(rule_id: int) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM rules WHERE id = ?", (rule_id,))
        conn.commit()


def duplicate_profile(source_profile_id: int, new_name: str, new_description: str = "") -> int | None:
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, description
            FROM profiles
            WHERE id = ?
        """, (source_profile_id,))
        profile_row = cursor.fetchone()

        if not profile_row:
            return None

        source_name, source_description = profile_row
        description_to_use = new_description if new_description else f"Copy of {source_name}: {source_description or ''}".strip()

        cursor.execute("""
            INSERT INTO profiles (name, description, is_builtin, created_at, updated_at)
            VALUES (?, ?, 0, datetime('now'), datetime('now'))
        """, (new_name, description_to_use))

        new_profile_id = cursor.lastrowid

        cursor.execute("""
            SELECT rule_type, target_type, pattern, enabled, priority, notes
            FROM rules
            WHERE profile_id = ?
        """, (source_profile_id,))
        source_rules = cursor.fetchall()

        for rule_type, target_type, pattern, enabled, priority, notes in source_rules:
            cursor.execute("""
                INSERT INTO rules (profile_id, rule_type, target_type, pattern, enabled, priority, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (new_profile_id, rule_type, target_type, pattern, enabled, priority, notes))

        conn.commit()
        return new_profile_id