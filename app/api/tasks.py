from fastapi import APIRouter, HTTPException
from typing import Optional
from app.database.database import list_tasks, get_task

router = APIRouter(prefix="/api", tags=["Tasks"])

@router.get("/tasks")
async def get_tasks(limit: int = 50):
    """Lists all active, completed, and pending agentic tasks."""
    return {"tasks": list_tasks(limit)}

@router.get("/tasks/{task_id}")
async def get_task_by_id(task_id: str):
    """Gets detailed task status, plan steps, and execution outputs."""
    task = get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")
    return task
