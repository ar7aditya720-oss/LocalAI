import os
from typing import Dict, Any

class AgentVerifier:
    @staticmethod
    def verify_file_deliverable(filepath: str) -> Dict[str, Any]:
        if not os.path.exists(filepath):
            return {"valid": False, "reason": f"File does not exist: {filepath}"}
            
        file_size = os.path.getsize(filepath)
        if file_size == 0:
            return {"valid": False, "reason": "File is empty (0 bytes)"}
            
        return {
            "valid": True,
            "filepath": filepath,
            "size_bytes": file_size,
            "status": "VERIFIED_VALID"
        }

agent_verifier = AgentVerifier()
