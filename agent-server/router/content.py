from pathlib import Path
import time
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse

from db.user import User
from schemas.content import QueryRequest, ReportRequest
from services.file_service import file_path, list_files, save_upload
from services.knowledge_service import generate_report, query_documents
from utils.auth import get_current_user
from utils.response import success_response

router = APIRouter(tags=["knowledge"])
_tasks: dict[str, dict] = {}


@router.post("/api/v1/upload/")
async def upload_document(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    info = await save_upload(current_user.user_id, file)
    task_id = str(uuid4())
    _tasks[task_id] = {
        "task_id": task_id,
        "status": "completed",
        "filename": info.filename,
        "step": "stored",
        "chunks": 1 if Path(info.filename).suffix.lower() == ".txt" else 0,
        "created_at": str(int(time.time())),
    }
    return success_response("File uploaded", {"task_id": task_id, "status": "completed", "filename": info.filename})


@router.get("/api/v1/upload/task/{task_id}")
async def get_task_status(task_id: str, _: User = Depends(get_current_user)):
    task = _tasks.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload task not found")
    return success_response("Task status retrieved", task)


@router.get("/api/v1/files/")
async def get_files(current_user: User = Depends(get_current_user)):
    return success_response("Files retrieved", {"files": list_files(current_user.user_id)})


@router.get("/api/v1/files/{filename}")
async def get_file_info(filename: str, current_user: User = Depends(get_current_user)):
    path = file_path(current_user.user_id, filename)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return success_response("File information retrieved", {"filename": path.name, "size": path.stat().st_size})


@router.delete("/api/v1/files/{filename}")
async def delete_file(filename: str, current_user: User = Depends(get_current_user)):
    path = file_path(current_user.user_id, filename)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    path.unlink()
    return success_response("File deleted", {"success": True, "message": "File deleted"})


@router.get("/api/v1/download/{filename}")
async def download_file(filename: str, current_user: User = Depends(get_current_user)):
    path = file_path(current_user.user_id, filename)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(path, filename=path.name)


@router.post("/api/v1/query/")
async def query(request: QueryRequest, current_user: User = Depends(get_current_user)):
    return success_response("Query completed", query_documents(current_user.user_id, request.question, request.top_k))


@router.post("/api/v1/report/")
async def report(request: ReportRequest, _: User = Depends(get_current_user)):
    return success_response("Report generated", generate_report(request.report_type, request.parameters))
