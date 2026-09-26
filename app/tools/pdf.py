import fitz  # PyMuPDF
from typing import Dict, Any, List
import os

class PDFTool:
    @staticmethod
    def extract_text(pdf_path: str) -> Dict[str, Any]:
        if not os.path.exists(pdf_path):
            return {"error": f"File not found: {pdf_path}"}
        
        try:
            doc = fitz.open(pdf_path)
            full_text = ""
            pages_data = []
            is_scanned = True
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                if len(text.strip()) > 30:
                    is_scanned = False
                full_text += f"\n--- Page {page_num+1} ---\n" + text
                pages_data.append({
                    "page_number": page_num + 1,
                    "text_length": len(text),
                    "has_text": len(text.strip()) > 10
                })
            
            return {
                "total_pages": len(doc),
                "full_text": full_text.strip(),
                "is_scanned": is_scanned,
                "pages": pages_data,
                "metadata": doc.metadata
            }
        except Exception as e:
            return {"error": f"PDF processing error: {str(e)}"}

    @staticmethod
    def render_page_to_image(pdf_path: str, page_number: int = 1, output_image_path: str = None) -> str:
        """Renders a PDF page to a PNG image for OCR or Vision Model."""
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = fitz.open(pdf_path)
        if page_number < 1 or page_number > len(doc):
            page_number = 1
        
        page = doc[page_number - 1]
        pix = page.get_pixmap(dpi=200)
        
        if not output_image_path:
            output_image_path = pdf_path + f"_page_{page_number}.png"
            
        pix.save(output_image_path)
        return output_image_path
