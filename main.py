from database import initialize_database
from seed_data import seed_profiles, seed_rules
from ui.main_window import launch_app


def main() -> None:
    initialize_database()
    seed_profiles()
    seed_rules()
    launch_app()


if __name__ == "__main__":
    main()