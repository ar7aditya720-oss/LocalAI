from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import os
import uuid
from app.knowledge.search import knowledge_search
from app.knowledge.ingest import KnowledgeIngestor
from app.database.database import list_knowledge_docs
from app.config import KNOWLEDGE_BASE_DIR

router = APIRouter(prefix="/api", tags=["Knowledge Base"])

class SearchQuery(BaseModel):
    query: str
    top_k: Optional[int] = 3

@router.get("/knowledge/docs")
async def get_knowledge_documents():
    """Lists all documents ingested into the local RAG knowledge base."""
    return {"documents": list_knowledge_docs()}

@router.post("/knowledge/search")
async def search_knowledge(req: SearchQuery):
    """Performs semantic vector search against local organizational documents."""
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")
    results = knowledge_search.search(req.query, top_k=req.top_k or 3)
    return {"query": req.query, "results": results}

@router.post("/knowledge/ingest")
async def ingest_knowledge_file(file: UploadFile = File(...)):
    """Ingests a new SOP, technical manual, or report into the local RAG knowledge base."""
    try:
        filename = file.filename
        save_path = os.path.join(str(KNOWLEDGE_BASE_DIR), f"kb_{uuid.uuid4().hex[:6]}_{filename}")
        
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)
            
        res = KnowledgeIngestor.ingest_document(save_path, title=filename)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Knowledge ingestion failed: {str(e)}")
