from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED


def create_zip_from_results(
    project_folder: str,
    results: list[dict],
    output_zip_path: str,
    allowed_classifications: set[str] | None = None,
) -> tuple[int, int]:
    if allowed_classifications is None:
        allowed_classifications = {"include"}

    base_folder = Path(project_folder).resolve()
    output_zip = Path(output_zip_path).resolve()
    output_zip.parent.mkdir(parents=True, exist_ok=True)

    files_added = 0
    total_bytes = 0

    with ZipFile(output_zip, "w", compression=ZIP_DEFLATED) as zip_file:
        for item in results:
            if item["classification"] not in allowed_classifications:
                continue

            relative_path = item["relative_path"]
            file_path = base_folder / relative_path

            if not file_path.exists() or not file_path.is_file():
                continue

            zip_file.write(file_path, arcname=relative_path)
            files_added += 1
            total_bytes += item["size_bytes"]

    return files_added, total_bytes