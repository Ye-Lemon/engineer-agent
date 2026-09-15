import json
import time
import uuid
from email import message
from typing import Any

from fastapi import APIRouter, HTTPException, UploadFile

from config.redis_session import redis_client
from crud.user import get_user_by_userID
from services.file_service import save_upload
from utils import response

router = APIRouter(prefix="/api/v1/tasks", tags=["任务管理"])
TASK_KEY_PREFIX = "task:"
TASK_TTL_SECONDS = 24 * 60 * 60

@router.get("/{task_id}")
async def create_task(task_id: str):
    task = await create_task_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return response.success_response(message="任务状态", data=task)


async def create_task_id(db,user_id:int):
    result = await get_user_by_userID(db,user_id)
    if result is None:
        raise HTTPException(status_code=500,detail="用户ID不存在")
    task_id = str(uuid.uuid4())
    return task_id


async def file_task(user_id:int,file:UploadFile):
    fileinfo = await save_upload(user_id=user_id,upload=file)
