import sqlite3
import json
import time
from typing import List, Dict, Any, Optional
from app.config import DB_PATH

def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Tasks table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id TEXT PRIMARY KEY,
            prompt TEXT NOT NULL,
            agent_name TEXT DEFAULT 'General Agent',
            model_used TEXT,
            status TEXT DEFAULT 'pending',
            plan_steps TEXT,
            output_text TEXT,
            created_at REAL,
            completed_at REAL
        )
        """)
        
        # Files table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id TEXT PRIMARY KEY,
            filename TEXT NOT NULL,
            filepath TEXT NOT NULL,
            file_type TEXT,
            file_size INTEGER,
            is_generated INTEGER DEFAULT 0,
            upload_time REAL
        )
        """)
        
        # Audit Logs table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp REAL,
            formatted_time TEXT,
            event_type TEXT,
            action TEXT,
            status TEXT,
            details_json TEXT
        )
        """)
        
        # Knowledge Documents table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge_docs (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            filepath TEXT NOT NULL,
            content_summary TEXT,
            chunk_count INTEGER DEFAULT 0,
            ingested_at REAL
        )
        """)
        
        conn.commit()

# --- Task DB Helpers ---
def save_task(task_id: str, prompt: str, agent_name: str, model_used: str, status: str = "running", plan_steps: list = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO tasks (id, prompt, agent_name, model_used, status, plan_steps, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (task_id, prompt, agent_name, model_used, status, json.dumps(plan_steps or []), time.time()))
        conn.commit()

def update_task(task_id: str, status: str, output_text: str = None, plan_steps: list = None):
    with get_connection() as conn:
        cursor = conn.cursor()
        query = "UPDATE tasks SET status = ?, completed_at = ?"
        params = [status, time.time()]
        if output_text is not None:
            query += ", output_text = ?"
            params.append(output_text)
        if plan_steps is not None:
            query += ", plan_steps = ?"
            params.append(json.dumps(plan_steps))
        query += " WHERE id = ?"
        params.append(task_id)
        cursor.execute(query, params)
        conn.commit()

def get_task(task_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        if row:
            d = dict(row)
            d["plan_steps"] = json.loads(d["plan_steps"] or "[]")
            return d
        return None

def list_tasks(limit: int = 50) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        result = []
        for r in rows:
            d = dict(r)
            d["plan_steps"] = json.loads(d["plan_steps"] or "[]")
            result.append(d)
        return result

# --- File DB Helpers ---
def save_file(file_id: str, filename: str, filepath: str, file_type: str, file_size: int, is_generated: bool = False):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO files (id, filename, filepath, file_type, file_size, is_generated, upload_time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (file_id, filename, filepath, file_type, file_size, 1 if is_generated else 0, time.time()))
        conn.commit()

def list_files() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM files ORDER BY upload_time DESC")
        return [dict(r) for r in cursor.fetchall()]

# --- Audit DB Helpers ---
def log_audit(event_type: str, action: str, status: str, details: dict = None):
    now = time.time()
    formatted = time.strftime("%H:%M:%S", time.localtime(now))
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO audit_logs (timestamp, formatted_time, event_type, action, status, details_json)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (now, formatted, event_type, action, status, json.dumps(details or {})))
        conn.commit()

def get_audit_logs(limit: int = 100) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM audit_logs ORDER BY timestamp DESC LIMIT ?", (limit,))
        rows = cursor.fetchall()
        res = []
        for r in rows:
            d = dict(r)
            d["details"] = json.loads(d["details_json"] or "{}")
            res.append(d)
        return res

# --- Knowledge DB Helpers ---
def save_knowledge_doc(doc_id: str, title: str, filepath: str, summary: str, chunk_count: int):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO knowledge_docs (id, title, filepath, content_summary, chunk_count, ingested_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (doc_id, title, filepath, summary, chunk_count, time.time()))
        conn.commit()

def list_knowledge_docs() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM knowledge_docs ORDER BY ingested_at DESC")
        return [dict(r) for r in cursor.fetchall()]
