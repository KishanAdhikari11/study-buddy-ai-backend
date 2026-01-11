from pathlib import Path

from models import FileType

ALLOWED_FILE_EXTENSIONS = {
    FileType.Pdf.value,
    FileType.Ppt.value,
    FileType.Docx.value,
    FileType.Pptx.value,
}


def ensure_directory_exists(directory_path: str) -> None:
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise RuntimeError(f"Failed to create directory {directory_path}: {e}")


def validate_file_extension(file_name: str) -> FileType:
    ext = Path(file_name).suffix.lower().lstrip(".")
    if ext not in ALLOWED_FILE_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {ext}")
    return FileType(ext)
