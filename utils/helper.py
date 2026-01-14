import os
import tempfile
from pathlib import Path
from typing import Awaitable, Callable, TypeVar

from models import FileType

ALLOWED_FILE_EXTENSIONS = {
    FileType.Pdf.value,
    FileType.Docx.value,
    FileType.Pptx.value,
}


T = TypeVar("T")


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


async def with_temp_file(
    contents: bytes,
    suffix: str,
    callback: Callable[[str], Awaitable[T]],
) -> T:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(contents)
            tmp_path = tmp.name

        return await callback(tmp_path)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
