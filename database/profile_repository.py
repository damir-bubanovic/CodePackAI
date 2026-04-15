from database import get_connection


def fetch_all_profiles():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, is_builtin
            FROM profiles
            ORDER BY is_builtin DESC, name ASC
        """)
        return cursor.fetchall()


def fetch_profile_by_name(profile_name: str):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, is_builtin, created_at, updated_at
            FROM profiles
            WHERE name = ?
        """, (profile_name,))
        return cursor.fetchone()


def fetch_profile_by_id(profile_id: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, name, description, is_builtin, created_at, updated_at
            FROM profiles
            WHERE id = ?
        """, (profile_id,))
        return cursor.fetchone()


def insert_profile(name: str, description: str = "", is_builtin: int = 0) -> int:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO profiles (name, description, is_builtin, created_at, updated_at)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        """, (name, description, is_builtin))
        conn.commit()
        return cursor.lastrowid


def update_profile_record(profile_id: int, name: str, description: str) -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE profiles
            SET name = ?, description = ?, updated_at = datetime('now')
            WHERE id = ?
        """, (name, description, profile_id))
        conn.commit()


def delete_profile_record(profile_id: int) -> bool:
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


def duplicate_profile_record(
    source_profile_id: int,
    new_name: str,
    new_description: str = "",
) -> tuple[int | None, list[tuple]]:

    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT name, description
            FROM profiles
            WHERE id = ?
        """, (source_profile_id,))
        profile_row = cursor.fetchone()

        if not profile_row:
            return None, []

        source_name, source_description = profile_row
        description_to_use = (
            new_description
            if new_description
            else f"Copy of {source_name}: {source_description or ''}".strip()
        )

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

        conn.commit()
        return new_profile_id, source_rules