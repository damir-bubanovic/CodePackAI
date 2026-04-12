from database import get_connection


def get_all_profiles():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description FROM profiles")
        return cursor.fetchall()


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
            ORDER BY priority ASC
        """, (profile_id,))

        return cursor.fetchall()