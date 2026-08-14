from urllib.parse import quote


def attachment_disposition(filename: str) -> str:
    safe_ascii = filename.encode("ascii", "ignore").decode() or "download"
    return (
        f'attachment; filename="{safe_ascii}"; '
        f"filename*=UTF-8''{quote(filename)}"
    )
