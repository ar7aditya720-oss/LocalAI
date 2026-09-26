from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import os
import uuid
import time
from app.config import WORKSPACE_DIR
from app.database.database import save_file, list_files
from app.security.audit import record_audit_event

router = APIRouter(prefix="/api", tags=["Files"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    """Uploads a local document/image file to the LocalAI workspace."""
    try:
        file_id = f"file_{uuid.uuid4().hex[:8]}"
        filename = file.filename
        ext = os.path.splitext(filename)[1].lower()
        
        save_path = os.path.join(str(WORKSPACE_DIR), f"{file_id}_{filename}")
        
        content = await file.read()
        with open(save_path, "wb") as f:
            f.write(content)
            
        file_size = len(content)
        save_file(file_id, filename, save_path, ext, file_size, is_generated=False)
        
        record_audit_event(
            event_type="FILE_UPLOAD",
            action=f"Uploaded file '{filename}' ({file_size} bytes)",
            status="SUCCESS",
            details={"file_id": file_id, "file_path": save_path}
        )
        
        return {
            "status": "SUCCESS",
            "file_id": file_id,
            "filename": filename,
            "filepath": save_path,
            "file_size": file_size,
            "extension": ext
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@router.get("/files")
async def get_all_files():
    """Lists all uploaded and generated files in the workspace."""
    return {"files": list_files()}

@router.get("/files/download/{filename}")
async def download_file(filename: str):
    """Downloads or views a file from the workspace."""
    filepath = os.path.join(str(WORKSPACE_DIR), filename)
    if not os.path.exists(filepath):
        # Search if prefixed with file_id
        matching = [f for f in os.listdir(str(WORKSPACE_DIR)) if f.endswith(filename)]
        if matching:
            filepath = os.path.join(str(WORKSPACE_DIR), matching[0])
        else:
            raise HTTPException(status_code=404, detail="File not found in workspace.")
            
    return FileResponse(filepath, filename=filename)
