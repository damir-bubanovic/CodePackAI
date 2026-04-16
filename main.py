from database import initialize_database
from ui.main_window import launch_app


def main() -> None:
    initialize_database()
    launch_app()


if __name__ == "__main__":
    main()