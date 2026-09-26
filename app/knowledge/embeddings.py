import math
from typing import List, Dict, Any

try:
    from sentence_transformers import SentenceTransformer
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

class LocalEmbeddings:
    def __init__(self):
        self._model = None
        self._initialized = False

    def _get_model(self):
        if not self._initialized:
            self._initialized = True
            if HAS_SENTENCE_TRANSFORMERS:
                try:
                    self._model = SentenceTransformer("all-MiniLM-L6-v2")
                except Exception as e:
                    print(f"[LocalEmbeddings Warning]: SentenceTransformer load fallback ({e}).")
        return self._model

    def get_embedding(self, text: str) -> List[float]:
        """Generates local embeddings without external API calls."""
        model = self._get_model()
        if model:
            try:
                emb = model.encode(text)
                return emb.tolist()
            except Exception:
                pass
            
        # Deterministic lightweight term-frequency embedding fallback
        words = text.lower().split()
        vec = [0.0] * 64
        for w in words:
            h = hash(w) % 64
            vec[h] += 1.0
        norm = math.sqrt(sum(x*x for x in vec)) or 1.0
        return [x / norm for x in vec]

local_embeddings = LocalEmbeddings()
