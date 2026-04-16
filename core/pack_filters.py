def filter_results(
    results,
    allowed_classifications,
    max_size_bytes=None,
    size_review_only=True,
):
    filtered = []
    skipped_large = []

    for r in results:
        classification = r["classification"]

        if classification not in allowed_classifications:
            continue

        if max_size_bytes is None:
            filtered.append(r)
            continue

        if size_review_only:
            if classification == "include":
                filtered.append(r)
            elif classification == "review":
                if r["size_bytes"] <= max_size_bytes:
                    filtered.append(r)
                else:
                    skipped_large.append(r)
        else:
            if r["size_bytes"] <= max_size_bytes:
                filtered.append(r)
            else:
                skipped_large.append(r)

    skipped_large = sorted(
        skipped_large,
        key=lambda x: x["size_bytes"],
        reverse=True
    )

    return filtered, skipped_large