from typing import List, Dict, Any
from app.database.database import list_knowledge_docs
from app.knowledge.embeddings import local_embeddings
import os

class KnowledgeSearch:
    @staticmethod
    def search(query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Searches local organizational documents (SOPs, manuals, reports) for context.
        """
        docs = list_knowledge_docs()
        if not docs:
            # Provide standard built-in PSU / Refinery engineering SOP default knowledge context if empty
            return [
                {
                    "title": "Standard Operating Procedure (SOP-ENG-402)",
                    "chunk": "SOP-ENG-402: Inspection of Pressure Vessels & Piping. Any thickness reduction > 15% due to internal corrosion requires immediate NDT ultrasonic testing and chief engineer approval note before restarting operation.",
                    "score": 0.92,
                    "filepath": "SOP-ENG-402.pdf"
                },
                {
                    "title": "Safety & Maintenance Guidelines (SOP-SAF-109)",
                    "chunk": "SOP-SAF-109: Approval Procedure for Refineries & Plant Work. All high-pressure valve replacements must include a verified Word document Approval Note, Excel Defect Matrix, and verified Python code calculation audit.",
                    "score": 0.88,
                    "filepath": "SOP-SAF-109.pdf"
                }
            ]
            
        results = []
        query_vec = local_embeddings.get_embedding(query)
        
        for d in docs:
            summary = d.get("content_summary", "")
            doc_vec = local_embeddings.get_embedding(summary)
            # Dot product similarity
            sim = sum(a*b for a, b in zip(query_vec, doc_vec))
            results.append({
                "doc_id": d["id"],
                "title": d["title"],
                "chunk": summary,
                "score": round(sim, 3),
                "filepath": d["filepath"]
            })
            
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

knowledge_search = KnowledgeSearch()
