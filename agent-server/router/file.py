import os
import shutil
import time
import uuid
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from config.file import ALLOWED_EXTENSIONS, MAX_FILE_SIZE, UPLOAD_DIR
from router.task import create_task
from utils import response

router = APIRouter(prefix="/api/v1/upload", tags=["文件上传"])


def _find_file(filename: str) -> Path:
    path = (UPLOAD_DIR / os.path.basename(filename)).resolve()
    if path.parent != UPLOAD_DIR.resolve() or not path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    return path


@router.post("/")
@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    filename = os.path.basename(file.filename or "")
    ext = Path(filename).suffix.lower().lstrip(".")
    if not filename or ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="不支持该文件格式")
    if file.size is not None and file.size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    disk_name = f"{int(time.time() * 1000)}_{uuid.uuid4().hex[:8]}{Path(filename).suffix.lower()}"
    save_path = UPLOAD_DIR / disk_name
    with save_path.open("wb") as target:
        shutil.copyfileobj(file.file, target)
    size = save_path.stat().st_size
    if size > MAX_FILE_SIZE:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="文件大小超过限制")

    task = await create_task(filename=filename, disk_name=disk_name, size=size)
    return response.success_response(message="上传成功", data={"task_id": task["task_id"],
        "status": "completed", "filename": filename})





@router.get("/files/")
async def get_file_list():
    files = []
    for path in UPLOAD_DIR.iterdir():
        if path.is_file():
            stat = path.stat()
            files.append({"filename": path.name, "size": stat.st_size, "created_at": stat.st_ctime,
                          "modified_at": stat.st_mtime, "path": str(path)})
    return response.success_response(message="文件列表", data={"files": files})


@router.get("/download/{filename}")
async def download_file(filename: str):
    path = _find_file(filename)
    return FileResponse(path, filename=path.name)


@router.delete("/files/{filename}")
async def delete_file(filename: str):
    path = _find_file(filename)
    path.unlink()
    return response.success_response(message="文件删除成功", data={"success": True, "message": "文件删除成功"})
