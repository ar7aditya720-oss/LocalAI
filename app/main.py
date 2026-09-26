from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import asyncio
from contextlib import asynccontextmanager

from app.config import APP_TITLE, VERSION, FRONTEND_DIR, WORKSPACE_DIR
from app.database.database import init_db
from app.security.audit import record_audit_event
from app.models.adapters import OllamaAdapter
from app.config import OLLAMA_BASE_URL

# API Routers
from app.api.chat import router as chat_router
from app.api.files import router as files_router
from app.api.tasks import router as tasks_router
from app.api.models import router as models_router
from app.api.agents import router as agents_router
from app.api.knowledge import router as knowledge_router
from app.api.system import router as system_router
from app.api.logs import router as logs_router

async def warm_up_local_models():
    """Warms up local Ollama model in VRAM in background for ultra-fast first response."""
    try:
        adapter = OllamaAdapter(base_url=OLLAMA_BASE_URL)
        # Background warmup
        await adapter.generate("Hello", model_name="llama3.1:latest", max_tokens=5)
        print("  [✓] Local AI Model Warmed Up in GPU VRAM (Zero-Latency Ready)")
    except Exception as e:
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup initialization
    init_db()
    record_audit_event("SYSTEM_STARTUP", "LocalAI FastAPI backend initialized successfully", "SUCCESS")
    print(f"==================================================")
    print(f"  LocalAI Backend Services Initialized (v{VERSION})")
    print(f"  Sovereign Air-Gapped Mode: ACTIVE")
    print(f"==================================================")
    
    # Launch model warm-up in background task
    asyncio.create_task(warm_up_local_models())
    
    yield
    record_audit_event("SYSTEM_SHUTDOWN", "LocalAI FastAPI backend stopped", "SHUTDOWN")

app = FastAPI(title=APP_TITLE, version=VERSION, lifespan=lifespan)

# Enable CORS for local origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(chat_router)
app.include_router(files_router)
app.include_router(tasks_router)
app.include_router(models_router)
app.include_router(agents_router)
app.include_router(knowledge_router)
app.include_router(system_router)
app.include_router(logs_router)

# Mount Workspace directory for downloaded/generated files
app.mount("/workspace", StaticFiles(directory=str(WORKSPACE_DIR)), name="workspace")

# Serve Frontend static files
index_html_path = FRONTEND_DIR / "index.html"
if index_html_path.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(index_html_path)

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "app": "LocalAI Sovereign Workbench",
        "version": VERSION,
        "mode": "Air-gapped / Local"
    }
