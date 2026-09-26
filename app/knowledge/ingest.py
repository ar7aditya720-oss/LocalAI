import os
from typing import List, Dict, Any
from app.tools.pdf import PDFTool
from app.tools.ocr import OCRTool
from app.database.database import save_knowledge_doc
from app.config import KNOWLEDGE_BASE_DIR
import docx

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i+chunk_size])
        chunks.append(chunk)
        i += (chunk_size - overlap)
    return chunks

class KnowledgeIngestor:
    @staticmethod
    def ingest_document(file_path: str, title: str = None) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            return {"error": f"File not found: {file_path}"}
            
        filename = os.path.basename(file_path)
        title = title or filename
        ext = os.path.splitext(filename)[1].lower()
        
        extracted_text = ""
        
        if ext == ".pdf":
            pdf_res = PDFTool.extract_text(file_path)
            if pdf_res.get("is_scanned"):
                img_path = PDFTool.render_page_to_image(file_path, 1)
                ocr_res = OCRTool.perform_ocr(img_path)
                extracted_text = ocr_res.get("extracted_text", "")
            else:
                extracted_text = pdf_res.get("full_text", "")
        elif ext in [".docx", ".doc"]:
            doc = docx.Document(file_path)
            extracted_text = "\n".join([p.text for p in doc.paragraphs if p.text])
        else:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                extracted_text = f.read()
                
        chunks = chunk_text(extracted_text)
        doc_id = f"doc_{os.urandom(4).hex()}"
        
        summary = extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
        save_knowledge_doc(doc_id, title, file_path, summary, len(chunks))
        
        return {
            "doc_id": doc_id,
            "title": title,
            "filename": filename,
            "chunk_count": len(chunks),
            "summary": summary,
            "status": "INGESTED"
        }
