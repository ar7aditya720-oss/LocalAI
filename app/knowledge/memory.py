import json
import os
import re
import time
import hashlib
from typing import Dict, Any, Optional, Tuple, List
from app.config import WORKSPACE_DIR, DB_PATH
import sqlite3

MEMORY_FILE_PATH = os.path.join(str(WORKSPACE_DIR), "device_memory.json")

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_memory_table():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS device_memory (
            id TEXT PRIMARY KEY,
            normalized_prompt TEXT NOT NULL,
            file_signature TEXT DEFAULT '',
            prompt_tokens TEXT,
            output_text TEXT NOT NULL,
            agent_name TEXT,
            hit_count INTEGER DEFAULT 1,
            created_at REAL,
            last_accessed REAL
        )
        """)
        conn.commit()

class PatternMemoryEngine:
    """
    On-device pattern recognition memory engine.
    Uses normalized string matching, token overlap, and file signature hashing to provide
    ultra-fast (< 50ms) responses for recognized patterns.
    """
    def __init__(self):
        init_memory_table()

    def normalize_text(self, text: str) -> str:
        """Cleans and normalizes text for pattern matching."""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s]', ' ', text)
        words = text.split()
        return " ".join(words)

    def calculate_similarity(self, prompt1: str, prompt2: str) -> float:
        """
        Calculates string matching similarity ratio using Token Set Overlap and Jaccard distance.
        """
        norm1 = self.normalize_text(prompt1)
        norm2 = self.normalize_text(prompt2)

        if norm1 == norm2:
            return 1.0

        set1 = set(norm1.split())
        set2 = set(norm2.split())

        if not set1 or not set2:
            return 0.0

        intersection = set1.intersection(set2)
        union = set1.union(set2)

        jaccard = len(intersection) / float(len(union))
        
        # Length penalty/bonus
        len_ratio = min(len(norm1), len(norm2)) / max(len(norm1), len(norm2))
        
        return round((jaccard * 0.7) + (len_ratio * 0.3), 3)

    def compute_file_signature(self, file_paths: List[str]) -> str:
        """Generates a signature hash for attached files."""
        if not file_paths:
            return ""
        sig = ""
        for fp in file_paths:
            if os.path.exists(fp):
                size = os.path.getsize(fp)
                filename = os.path.basename(fp)
                sig += f"{filename}_{size}_"
        return hashlib.md5(sig.encode('utf-8')).hexdigest()

    def find_matching_pattern(self, prompt: str, file_paths: List[str] = None, min_threshold: float = 0.95) -> Optional[Dict[str, Any]]:
        """
        Searches device memory for pattern recognition match using string matching algorithms.
        """
        file_sig = self.compute_file_signature(file_paths or [])
        norm_input = self.normalize_text(prompt)

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM device_memory ORDER BY hit_count DESC, last_accessed DESC")
            records = cursor.fetchall()

            best_match = None
            best_score = 0.0

            for row in records:
                db_norm = row["normalized_prompt"]
                db_sig = row["file_signature"] or ""

                # If file signature matches exactly and prompt is similar
                file_match_bonus = 0.2 if (file_sig and file_sig == db_sig) else 0.0
                
                score = self.calculate_similarity(norm_input, db_norm) + file_match_bonus

                if score > best_score:
                    best_score = score
                    best_match = row

            if best_match and best_score >= min_threshold:
                # Increment hit count & update access time
                cursor.execute("""
                UPDATE device_memory 
                SET hit_count = hit_count + 1, last_accessed = ? 
                WHERE id = ?
                """, (time.time(), best_match["id"]))
                conn.commit()

                return {
                    "memory_id": best_match["id"],
                    "output_text": best_match["output_text"],
                    "agent_name": best_match["agent_name"],
                    "similarity_score": min(best_score, 1.0),
                    "hit_count": best_match["hit_count"] + 1,
                    "matched_pattern": best_match["normalized_prompt"]
                }

        return None

    def store_pattern(self, prompt: str, output_text: str, agent_name: str = "Industrial Analyst", file_paths: List[str] = None):
        """
        Saves a newly processed prompt & output pattern into local device memory.
        """
        norm_prompt = self.normalize_text(prompt)
        if not norm_prompt or len(norm_prompt) < 3:
            return

        file_sig = self.compute_file_signature(file_paths or [])
        memory_id = f"mem_{hashlib.md5((norm_prompt + file_sig).encode('utf-8')).hexdigest()[:10]}"
        now = time.time()

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO device_memory (id, normalized_prompt, file_signature, prompt_tokens, output_text, agent_name, hit_count, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                output_text = excluded.output_text,
                hit_count = hit_count + 1,
                last_accessed = excluded.last_accessed
            """, (memory_id, norm_prompt, file_sig, norm_prompt, output_text, agent_name, now, now))
            conn.commit()

        # Sync to local JSON file for backup
        self.sync_json_backup()

    def sync_json_backup(self):
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, normalized_prompt, agent_name, hit_count, created_at FROM device_memory LIMIT 200")
                rows = [dict(r) for r in cursor.fetchall()]
            with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(rows, f, indent=2)
        except Exception as e:
            print(f"[PatternMemoryEngine Backup Warning]: {e}")

pattern_memory = PatternMemoryEngine()
