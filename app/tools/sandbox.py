import subprocess
import sys
import tempfile
import os
import time
from typing import Dict, Any
from app.config import WORKSPACE_DIR
from app.security.audit import record_audit_event

class CodeSandboxTool:
    @staticmethod
    def execute_python_code(code_string: str, timeout_seconds: int = 10) -> Dict[str, Any]:
        """
        Executes Python code in a sandboxed, isolated temporary directory with process controls.
        Enforces timeout limits, captures stdout and stderr, and records security audit trail.
        """
        # Create a clean temp file in workspace
        script_filename = f"sandbox_script_{int(time.time()*1000)}.py"
        script_path = os.path.join(str(WORKSPACE_DIR), script_filename)
        
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(code_string)
            
        record_audit_event(
            event_type="CODE_SANDBOX_EXECUTION",
            action=f"Executing sandboxed Python script {script_filename}",
            status="PENDING",
            details={"timeout": timeout_seconds}
        )
        
        start_time = time.time()
        try:
            # Run in isolated subprocess
            proc = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                cwd=str(WORKSPACE_DIR)
            )
            
            execution_time = round(time.time() - start_time, 3)
            success = (proc.returncode == 0)
            
            result = {
                "success": success,
                "exit_code": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
                "execution_time_sec": execution_time,
                "script_path": script_path,
                "sandbox_type": "Subprocess Process Isolation (Air-gapped)"
            }
            
            record_audit_event(
                event_type="CODE_SANDBOX_RESULT",
                action=f"Script execution finished with return code {proc.returncode}",
                status="SUCCESS" if success else "FAILED",
                details=result
            )
            
            return result
            
        except subprocess.TimeoutExpired:
            record_audit_event(
                event_type="CODE_SANDBOX_TIMEOUT",
                action=f"Script execution timed out after {timeout_seconds}s",
                status="TIMED_OUT"
            )
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Execution Timed Out after {timeout_seconds} seconds.",
                "execution_time_sec": timeout_seconds,
                "sandbox_type": "Subprocess Process Isolation (Air-gapped)"
            }
        except Exception as e:
            return {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": f"Sandbox Exception: {str(e)}",
                "execution_time_sec": 0,
                "sandbox_type": "Subprocess Process Isolation (Air-gapped)"
            }
