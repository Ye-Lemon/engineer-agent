from pathlib import Path
import time
import json
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import FileResponse
from db.user import User
from schemas.content import QueryRequest, ReportRequest
from services.file_service import file_path, list_files, save_upload
from services.knowledge_service import generate_report, query_documents
from utils.auth import auth_user_info
from utils.response import success_response
from config.redis_session import redis_client

router = APIRouter(tags=["knowledge"])
TASK_KEY_PREFIX = "engineering_agent:task:"
TASK_TTL_SECONDS = 24 * 60 * 60


@router.post("/api/v1/upload/")
async def upload_document(file: UploadFile = File(...), current_user: User = Depends(auth_user_info)):
    info = await save_upload(current_user.user_id, file)
    task_id = str(uuid4())
    task = {
        "task_id": task_id,
        "status": "已完成",
        "filename": info.filename,
        "step": "已入库",
        "chunks": 1 if Path(info.filename).suffix.lower() == ".txt" else 0,
        "created_at": str(int(time.time())),
    }
    await redis_client.setex(f"{TASK_KEY_PREFIX}{task_id}", TASK_TTL_SECONDS, json.dumps(task))
    return success_response("文件已上传", {"task_id": task_id, "status": "completed", "filename": info.filename})


@router.get("/api/v1/upload/task/{task_id}")
async def get_task_status(task_id: str, _: User = Depends(auth_user_info)):
    value = await redis_client.get(f"{TASK_KEY_PREFIX}{task_id}")
    task = json.loads(value) if value else None
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Upload task not found")
    return success_response("Task status retrieved", task)


@router.get("/api/v1/files/")
async def get_files(current_user: User = Depends(auth_user_info)):
    return success_response("Files retrieved", {"files": list_files(current_user.user_id)})


@router.get("/api/v1/files/{filename}")
async def get_file_info(filename: str, current_user: User = Depends(auth_user_info)):
    path = file_path(current_user.user_id, filename)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return success_response("File information retrieved", {"filename": path.name, "size": path.stat().st_size})


@router.delete("/api/v1/files/{filename}")
async def delete_file(filename: str, current_user: User = Depends(auth_user_info)):
    path = file_path(current_user.user_id, filename)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    path.unlink()
    return success_response("File deleted", {"success": True, "message": "File deleted"})


@router.get("/api/v1/download/{filename}")
async def download_file(filename: str, current_user: User = Depends(auth_user_info)):
    path = file_path(current_user.user_id, filename)
    if not path.is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    return FileResponse(path, filename=path.name)


@router.post("/api/v1/query/")
async def query(request: QueryRequest, current_user: User = Depends(auth_user_info)):
    return success_response("Query completed", query_documents(current_user.user_id, request.question, request.top_k))


@router.post("/api/v1/report/")
async def report(request: ReportRequest, _: User = Depends(auth_user_info)):
    return success_response("Report generated", generate_report(request.report_type, request.parameters))

