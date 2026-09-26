from typing import Dict, Any, List
from app.models.adapters import OllamaAdapter
from app.config import DEFAULT_MODELS, OLLAMA_BASE_URL
from app.security.audit import record_audit_event

class ModelRouter:
    def __init__(self):
        self.adapter = OllamaAdapter(base_url=OLLAMA_BASE_URL)
        self.available_models = []

    async def refresh_available_models(self) -> List[Dict[str, Any]]:
        models = await self.adapter.list_models()
        self.available_models = models
        return models

    def route_task(self, prompt: str, file_types: List[str] = None, agent_hint: str = None) -> Dict[str, Any]:
        """
        Determines the optimal local model based on prompt content, file attachments, and agent hints.
        """
        file_types = file_types or []
        lower_p = prompt.lower()

        # Rule 1: Coding tasks
        coding_keywords = ["code", "debug", "python", "java", "c++", "script", "function", "fix bug", "compile", "algorithm", "syntax"]
        is_coding = any(kw in lower_p for kw in coding_keywords) or any(ft in [".py", ".java", ".cpp", ".js", ".c"] for ft in file_types)

        # Rule 2: Image / Vision tasks
        is_vision = any(ft in [".png", ".jpg", ".jpeg", ".bmp"] for ft in file_types) or any(kw in lower_p for kw in ["image", "drawing", "ocr", "diagram", "scanned", "photo", "p&id"])

        # Rule 3: Math / Engineering calculation
        is_math = any(kw in lower_p for kw in ["calculate", "formula", "math", "equation", "corrosion rate", "wall thickness", "stress"])

        # Determine target model
        if is_coding or agent_hint == "Coding Agent":
            selected_model = DEFAULT_MODELS["coding"] # qwen2.5-coder:7b
            capability = "Coding & Script Execution"
        elif is_math:
            selected_model = DEFAULT_MODELS["math"] # mightykatun/qwen2.5-math:7b
            capability = "Mathematical & Engineering Calculations"
        elif is_vision or agent_hint == "Multimodal Agent":
            selected_model = DEFAULT_MODELS["vision"] # llama3.1:latest
            capability = "Vision & Image Analysis"
        elif len(prompt) < 100 and not file_types:
            selected_model = DEFAULT_MODELS["fast"] # llama3.2:latest
            capability = "Fast Lightweight Reasoning"
        else:
            selected_model = DEFAULT_MODELS["reasoning"] # llama3.1:latest
            capability = "General Reasoning & Document Synthesis"

        record_audit_event(
            event_type="MODEL_ROUTING",
            action=f"Routed prompt to model '{selected_model}'",
            status="SUCCESS",
            details={"prompt_length": len(prompt), "capability": capability, "model": selected_model}
        )

        return {
            "selected_model": selected_model,
            "capability": capability,
            "runtime": "Ollama (Local GPU/CPU)",
            "air_gapped": True
        }

model_router = ModelRouter()
