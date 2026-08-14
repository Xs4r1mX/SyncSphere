import mimetypes


def guess_content_type(filename: str, fallback: str = "application/octet-stream") -> str:
    content_type, _ = mimetypes.guess_type(filename)
    return content_type or fallback
