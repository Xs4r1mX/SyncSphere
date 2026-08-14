def file_action_flags(
    *,
    is_folder: bool,
    trashed: bool,
    web_view_link: str | None = None,
) -> tuple[bool, bool]:
    """Return (can_open, can_download) for a file list item."""
    can_download = not trashed and not is_folder
    can_open = not trashed and (not is_folder or bool(web_view_link))
    return can_open, can_download
