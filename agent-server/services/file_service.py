from pathlib import Path
import re
from typing import Iterable

import aiofiles
from fastapi import HTTPException, UploadFile, status

from schemas.content import FileInfo

UPLOAD_ROOT = Path(__file__).resolve().parents[1] / "data" / "uploads"
MAX_UPLOAD_SIZE = 100 * 1024 * 1024
ALLOWED_SUFFIXES = {
    ".pdf", ".doc", ".docx", ".txt", ".md", ".markdown", ".csv", ".tsv",
    ".json", ".html", ".htm", ".xhtml", ".xlsx", ".xls", ".pptx", ".ppt",
}


def user_upload_directory(user_id: int) -> Path:
    directory = UPLOAD_ROOT / str(user_id)
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def safe_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^A-Za-z0-9._-]", "_", name)
    if not name or name in {".", ".."}:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="无效文件名")
    if Path(name).suffix.lower() not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="文件格式不支持")
    return name


def file_path(user_id: int, filename: str) -> Path:
    return user_upload_directory(user_id) / safe_filename(filename)


async def save_upload(user_id: int, upload: UploadFile) -> FileInfo:
    filename = safe_filename(upload.filename or "")
    destination = file_path(user_id, filename)
    size = 0
    try:
        async with aiofiles.open(destination, "wb") as output:
            while chunk := await upload.read(1024 * 1024):
                size += len(chunk)
                if size > MAX_UPLOAD_SIZE:
                    raise HTTPException(413, "文件大小超过100MB")
                await output.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await upload.close()
    return build_file_info(destination)


def build_file_info(path: Path) -> FileInfo:
    stat = path.stat()
    return FileInfo(
        filename=path.name,
        size=stat.st_size,
        created_at=stat.st_ctime,
        modified_at=stat.st_mtime,
        path=str(path)
    )


def list_files(user_id: int) -> list[FileInfo]:
    directory = user_upload_directory(user_id)
    return [build_file_info(path) for path in sorted(directory.iterdir(), key=lambda item: item.stat().st_mtime, reverse=True) if path.is_file()]


def text_files(user_id: int) -> Iterable[Path]:
    return (path for path in user_upload_directory(user_id).glob("*.txt") if path.is_file())
