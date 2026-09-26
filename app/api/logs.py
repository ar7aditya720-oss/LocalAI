from fastapi import APIRouter
from app.security.audit import fetch_recent_audit_trail

router = APIRouter(prefix="/api", tags=["Audit Logs"])

@router.get("/logs")
async def get_audit_logs(limit: int = 50):
    """Retrieves local audit logging events."""
    logs = fetch_recent_audit_trail(limit)
    return {"logs": logs}
