from core.pack_filters import filter_results
from core.zip_utils import create_zip


def create_zip_from_results(
    project_folder: str,
    results,
    output_zip_path: str,
    allowed_classifications,
    max_size_bytes=None,
    size_review_only=True,
):
    filtered_results, skipped_large = filter_results(
        results=results,
        allowed_classifications=allowed_classifications,
        max_size_bytes=max_size_bytes,
        size_review_only=size_review_only,
    )

    files_added, total_bytes = create_zip(
        project_folder=project_folder,
        results=filtered_results,
        output_zip_path=output_zip_path,
    )

    return files_added, total_bytes