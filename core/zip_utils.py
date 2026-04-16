import zipfile
from pathlib import Path


def create_zip(
    project_folder: str,
    results,
    output_zip_path: str,
):
    base_path = Path(project_folder)

    files_added = 0
    total_bytes = 0

    with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as zipf:
        for r in results:
            abs_path = base_path / r["relative_path"]

            if not abs_path.exists():
                continue

            zipf.write(abs_path, arcname=r["relative_path"])

            files_added += 1
            total_bytes += r["size_bytes"]

    return files_added, total_bytes