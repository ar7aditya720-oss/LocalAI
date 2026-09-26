from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import time
from app.agent.executor import agent_executor
from app.database.database import get_task

router = APIRouter(prefix="/api", tags=["Chat & Agent"])

class ChatRequest(BaseModel):
    message: str
    agent: Optional[str] = "Industrial Analyst"
    model: Optional[str] = None
    file_ids: Optional[List[str]] = []
    file_paths: Optional[List[str]] = []

class ChatResponse(BaseModel):
    task_id: str
    reply: str
    status: str
    model_used: str
    agent_name: str
    plan_steps: List[Dict[str, Any]]
    generated_files: List[str]

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    """
    Main chat completion & agent execution endpoint.
    Accepts user prompts, file attachments, and agent/model preferences.
    """
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message prompt cannot be empty.")
        
    task_id = f"task_{uuid.uuid4().hex[:8]}"
    
    # Run agent workflow
    res = await agent_executor.run_agent_workflow(
        task_id=task_id,
        prompt=req.message,
        file_paths=req.file_paths,
        agent_name=req.agent or "Industrial Analyst",
        model_override=req.model
    )
    
    return ChatResponse(
        task_id=task_id,
        reply=res["output"],
        status=res["status"],
        model_used=res["model_used"],
        agent_name=res["agent_name"],
        plan_steps=res["plan_steps"],
        generated_files=res.get("generated_files", [])
    )
