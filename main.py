from database import initialize_database
from seed_data import seed_profiles, seed_rules


def main() -> None:
    initialize_database()
    seed_profiles()
    seed_rules()
    print("Database initialized, profiles seeded, and rules seeded.")


if __name__ == "__main__":
    main()