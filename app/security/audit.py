from app.database.database import log_audit, get_audit_logs

def record_audit_event(event_type: str, action: str, status: str = "SUCCESS", details: dict = None):
    """Logs an audit event to SQLite and system log."""
    log_audit(event_type, action, status, details)

def fetch_recent_audit_trail(limit: int = 50):
    return get_audit_logs(limit)
