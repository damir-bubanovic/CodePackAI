from pathlib import Path


def iter_files(project_folder: str):
    base_path = Path(project_folder)

    for path in base_path.rglob("*"):
        if path.is_file():
            yield path


def get_relative_path(base: Path, file_path: Path) -> str:
    return str(file_path.relative_to(base))


def get_file_size(file_path: Path) -> int:
    try:
        return file_path.stat().st_size
    except OSError:
        return 0