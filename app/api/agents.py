from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["Agents"])

@router.get("/agents")
async def list_agents():
    """Lists available specialized local agents."""
    agents = [
        {
            "id": "industrial_analyst",
            "name": "Industrial Analyst",
            "description": "Specialized in engineering documents, inspection reports, SOP compliance, P&ID review, and official approval notes.",
            "default_model": "llama3.1:latest",
            "capabilities": ["PDF Processing", "OCR", "SOP Retrieval", "Word Approval Notes"]
        },
        {
            "id": "coding_agent",
            "name": "Coding Agent",
            "description": "Generates, debugs, and runs code inside an isolated sandbox with automated test assertion verification.",
            "default_model": "qwen2.5-coder:7b",
            "capabilities": ["Code Generation", "Debugging", "Sandboxed Execution", "Test Verification"]
        },
        {
            "id": "multimodal_agent",
            "name": "Multimodal Agent",
            "description": "Processes photographs, scanned inspection sheets, handwritten notes, and engineering drawings.",
            "default_model": "llama3.1:latest",
            "capabilities": ["Image Understanding", "Scanned Document Analysis", "OpenCV Preprocessing"]
        },
        {
            "id": "governance_agent",
            "name": "Governance & Report Agent",
            "description": "Summarizes internal correspondence, prepares PSU board presentations, and creates Excel data matrices.",
            "default_model": "llama3.1:latest",
            "capabilities": ["Document Summarization", "PowerPoint Presentations", "Excel Spreadsheets"]
        }
    ]
    return {"agents": agents}
