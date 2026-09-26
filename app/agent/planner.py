from typing import List, Dict, Any

class AgentPlanner:
    @staticmethod
    def create_plan(prompt: str, file_types: List[str] = None, agent_name: str = None) -> List[Dict[str, Any]]:
        """
        Decomposes a user request into sequential execution steps.
        """
        file_types = file_types or []
        lower_p = prompt.lower()

        steps = []
        
        # Step 1: Request understanding & document parsing
        if file_types:
            steps.append({
                "step_num": 1,
                "action": "DOCUMENT_PROCESSING",
                "description": f"Parse uploaded attachment ({', '.join(file_types)}) using PyMuPDF / PIL",
                "status": "pending"
            })
            if any(ft in [".pdf", ".png", ".jpg", ".jpeg"] for ft in file_types):
                steps.append({
                    "step_num": 2,
                    "action": "OCR_VISION_ANALYSIS",
                    "description": "Inspect document for scanned text or technical diagrams; perform OCR if needed",
                    "status": "pending"
                })
        else:
            steps.append({
                "step_num": 1,
                "action": "INPUT_ANALYSIS",
                "description": "Analyze user prompt and extract requirements & context",
                "status": "pending"
            })

        # Step 2/3: Knowledge retrieval RAG
        steps.append({
            "step_num": len(steps) + 1,
            "action": "KNOWLEDGE_RETRIEVAL",
            "description": "Search local organizational knowledge base for SOPs, manuals, and precedent reports",
            "status": "pending"
        })

        # Step 3/4: Model routing & Local AI reasoning
        steps.append({
            "step_num": len(steps) + 1,
            "action": "MODEL_INFERENCE",
            "description": "Select local model (Reasoning/Coding/Vision) and perform on-premise inference",
            "status": "pending"
        })

        # Step 4/5: Deliverable generation or tool execution
        if "approval note" in lower_p or "word" in lower_p or "docx" in lower_p or "report" in lower_p:
            steps.append({
                "step_num": len(steps) + 1,
                "action": "GENERATE_DOCX",
                "description": "Generate official Word document Approval Note (.docx)",
                "status": "pending"
            })
        if "excel" in lower_p or "xlsx" in lower_p or "spreadsheet" in lower_p or "matrix" in lower_p:
            steps.append({
                "step_num": len(steps) + 1,
                "action": "GENERATE_XLSX",
                "description": "Generate Excel spreadsheet report matrix (.xlsx)",
                "status": "pending"
            })
        if "presentation" in lower_p or "powerpoint" in lower_p or "pptx" in lower_p or "slide" in lower_p:
            steps.append({
                "step_num": len(steps) + 1,
                "action": "GENERATE_PPTX",
                "description": "Generate PowerPoint slide deck presentation (.pptx)",
                "status": "pending"
            })
        if "code" in lower_p or "python" in lower_p or "debug" in lower_p or "script" in lower_p or agent_name == "Coding Agent":
            steps.append({
                "step_num": len(steps) + 1,
                "action": "SANDBOX_CODE_EXECUTION",
                "description": "Execute code inside isolated sandbox, run automated tests & verify output",
                "status": "pending"
            })

        # Final Step: Output Verification & Audit Logging
        steps.append({
            "step_num": len(steps) + 1,
            "action": "VERIFY_AND_AUDIT",
            "description": "Verify generated output integrity and record local audit log trace",
            "status": "pending"
        })

        return steps
