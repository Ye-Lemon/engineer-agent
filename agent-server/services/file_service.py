from pathlib import Path
import re
import time
from typing import Iterable

from fastapi import HTTPException, UploadFile, status

from schemas.content import FileInfo

UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "data" / "uploads"
MAX_UPLOAD_SIZE = 10 * 1024 * 1024
ALLOWED_SUFFIXES = {".pdf", ".doc", ".docx", ".txt"}


def user_upload_directory(user_id: int) -> Path:
    directory = UPLOAD_ROOT / str(user_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def safe_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not name or name in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid filename")
    if Path(name).suffix.lower() not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    return name


def file_path(user_id: int, filename: str) -> Path:
    return user_upload_directory(user_id) / safe_filename(filename)


async def save_upload(user_id: int, upload: UploadFile) -> FileInfo:
    filename = safe_filename(upload.filename or "")
    destination = file_path(user_id, filename)
    size = 0
    with destination.open("wb") as output:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_UPLOAD_SIZE:
                output.close()
                destination.unlink(missing_ok=True)
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File exceeds 10 MB")
            output.write(chunk)
    await upload.close()
    return build_file_info(destination)


def build_file_info(path: Path) -> FileInfo:
    stat = path.stat()
    return FileInfo(
        filename=path.name,
        size=stat.st_size,
        created_at=stat.st_ctime,
        modified_at=stat.st_mtime,
        path=path.name,
    )


def list_files(user_id: int) -> list[FileInfo]:
    directory = user_upload_directory(user_id)
    return [build_file_info(path) for path in sorted(directory.iterdir(), key=lambda item: item.stat().st_mtime, reverse=True) if path.is_file()]


def text_files(user_id: int) -> Iterable[Path]:
    return (path for path in user_upload_directory(user_id).glob("*.txt") if path.is_file())
