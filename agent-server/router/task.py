import time
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException

from utils import response

router = APIRouter(prefix="/api/v1/tasks", tags=["任务管理"])
_tasks: dict[str, dict[str, Any]] = {}


def create_task(*, filename: str, disk_name: str, size: int, status: str = "completed") -> dict[str, Any]:
    task = {"task_id": uuid.uuid4().hex, "status": status, "filename": filename,
            "disk_name": disk_name, "size": size, "created_at": time.time()}
    _tasks[task["task_id"]] = task
    return task


def get_task(task_id: str) -> dict[str, Any] | None:
    return _tasks.get(task_id)


@router.get("/{task_id}")
async def get_task_status(task_id: str):
    task = get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="任务不存在")
    return response.success_response(message="任务状态", data=task)
