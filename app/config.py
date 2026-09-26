import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# Paths
WORKSPACE_DIR = BASE_DIR / "workspace"
KNOWLEDGE_BASE_DIR = BASE_DIR / "knowledge_base"
LOGS_DIR = BASE_DIR / "logs"
DB_PATH = BASE_DIR / "localai.db"
FRONTEND_DIR = BASE_DIR / "frontend"

# Ensure directories exist
for folder in [WORKSPACE_DIR, KNOWLEDGE_BASE_DIR, LOGS_DIR, FRONTEND_DIR]:
    folder.mkdir(parents=True, exist_ok=True)

# Server Config
HOST = "0.0.0.0"
PORT = 8000
APP_TITLE = "LocalAI — Sovereign On-Premise Agentic AI Workbench"
VERSION = "1.0.0"

# Ollama Config
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Model Mappings & Capabilities
DEFAULT_MODELS = {
    "reasoning": "llama3.1:latest",
    "coding": "qwen2.5-coder:7b",
    "vision": "llama3.1:latest",
    "math": "mightykatun/qwen2.5-math:7b",
    "fast": "llama3.2:latest",
    "lightweight": "phi3:latest"
}

# Network Security
AIR_GAPPED_MODE = True
ALLOWED_EXTERNAL_CALLS = 0
