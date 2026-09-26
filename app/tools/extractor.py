import os
import re
from typing import Dict, Any
from app.tools.pdf import PDFTool
from app.tools.ocr import OCRTool
from app.tools.image import ImageTool

try:
    import docx
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import openpyxl
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False

class UniversalFileExtractor:
    @staticmethod
    def extract_file_content(filepath: str) -> Dict[str, Any]:
        """
        Extracts exact, comprehensive content from any uploaded file format.
        Supports HTML, TXT, MD, Code files, PDF, DOCX, XLSX, and Images.
        """
        if not os.path.exists(filepath):
            return {"error": f"File not found: {filepath}", "content": ""}

        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()
        size_kb = round(os.path.getsize(filepath) / 1024, 2)

        # 1. HTML / HTM Files
        if ext in [".html", ".htm"]:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    raw_html = f.read()

                # Extract Title
                title_match = re.search(r'<title[^>]*>(.*?)</title>', raw_html, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else "Untitled HTML Page"

                # Extract Headings
                headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', raw_html, re.IGNORECASE | re.DOTALL)
                clean_headings = [re.sub(r'<[^>]+>', '', h).strip() for h in headings if h.strip()]

                # Clean Body Text (strip scripts & style tags)
                body_clean = re.sub(r'<script[^>]*>.*?</script>', '', raw_html, flags=re.IGNORECASE | re.DOTALL)
                body_clean = re.sub(r'<style[^>]*>.*?</style>', '', body_clean, flags=re.IGNORECASE | re.DOTALL)
                text_content = re.sub(r'<[^>]+>', ' ', body_clean)
                text_content = re.sub(r'\s+', ' ', text_content).strip()

                # Summary snippet & markup preview
                parsed_summary = (
                    f"HTML File Name: {filename} ({size_kb} KB)\n"
                    f"Page Title: {title}\n"
                    f"Detected Headings ({len(clean_headings)}): {', '.join(clean_headings[:8])}\n"
                    f"Full Extracted Text Content:\n{text_content[:3000]}\n\n"
                    f"Raw HTML Structure Preview:\n{raw_html[:1500]}"
                )

                return {
                    "filename": filename,
                    "file_type": "HTML Document",
                    "title": title,
                    "extracted_text": parsed_summary,
                    "full_raw": raw_html,
                    "status": "SUCCESS"
                }
            except Exception as e:
                return {"filename": filename, "extracted_text": f"HTML read error: {e}", "status": "ERROR"}

        # 2. Text / Markdown / Code / JSON / Log Files
        elif ext in [".txt", ".md", ".json", ".csv", ".log", ".xml", ".yaml", ".yml", ".py", ".js", ".java", ".cpp", ".c", ".h", ".cs", ".php"]:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    text_content = f.read()
                
                content_str = (
                    f"Source File: {filename} (Type: {ext.upper()}, Size: {size_kb} KB)\n"
                    f"File Content:\n{text_content[:4000]}"
                )
                return {
                    "filename": filename,
                    "file_type": f"{ext.upper()} Code/Text File",
                    "extracted_text": content_str,
                    "full_raw": text_content,
                    "status": "SUCCESS"
                }
            except Exception as e:
                return {"filename": filename, "extracted_text": f"Text read error: {e}", "status": "ERROR"}

        # 3. PDF Files
        elif ext == ".pdf":
            pdf_res = PDFTool.extract_text(filepath)
            full_text = pdf_res.get("full_text", "")
            if pdf_res.get("is_scanned") or len(full_text.strip()) < 30:
                img_path = PDFTool.render_page_to_image(filepath, 1)
                ocr_res = OCRTool.perform_ocr(img_path)
                full_text = ocr_res.get("extracted_text", "")

            content_str = (
                f"PDF Document: {filename} ({pdf_res.get('total_pages', 1)} pages, {size_kb} KB)\n"
                f"Extracted Content:\n{full_text[:4000]}"
            )
            return {
                "filename": filename,
                "file_type": "PDF Document",
                "extracted_text": content_str,
                "status": "SUCCESS"
            }

        # 4. Word Documents (.docx)
        elif ext in [".docx", ".doc"] and HAS_DOCX:
            try:
                doc = docx.Document(filepath)
                paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                full_text = "\n".join(paragraphs)
                content_str = (
                    f"Word Document: {filename} ({len(paragraphs)} paragraphs, {size_kb} KB)\n"
                    f"Extracted Content:\n{full_text[:4000]}"
                )
                return {
                    "filename": filename,
                    "file_type": "Word Document",
                    "extracted_text": content_str,
                    "status": "SUCCESS"
                }
            except Exception as e:
                return {"filename": filename, "extracted_text": f"Docx error: {e}", "status": "ERROR"}

        # 5. Excel Spreadsheets (.xlsx)
        elif ext in [".xlsx", ".xls"] and HAS_OPENPYXL:
            try:
                wb = openpyxl.load_workbook(filepath, data_only=True)
                summary = f"Excel Workbook: {filename} (Sheets: {', '.join(wb.sheetnames)})\n"
                sheet = wb.active
                rows_summary = []
                for row in list(sheet.iter_rows(values_only=True))[:15]:
                    row_cells = [str(c) for c in row if c is not None]
                    if row_cells:
                        rows_summary.append(" | ".join(row_cells))
                summary += "Sample Data Rows:\n" + "\n".join(rows_summary)
                return {
                    "filename": filename,
                    "file_type": "Excel Workbook",
                    "extracted_text": summary,
                    "status": "SUCCESS"
                }
            except Exception as e:
                return {"filename": filename, "extracted_text": f"Excel error: {e}", "status": "ERROR"}

        # 6. Images (.png, .jpg, .jpeg)
        elif ext in [".png", ".jpg", ".jpeg"]:
            ocr_res = OCRTool.perform_ocr(filepath)
            img_info = ImageTool.inspect_image(filepath)
            content_str = (
                f"Image File: {filename} ({img_info.get('width')}x{img_info.get('height')} px, {size_kb} KB)\n"
                f"OCR Extracted Text:\n{ocr_res.get('extracted_text', '')}"
            )
            return {
                "filename": filename,
                "file_type": "Image",
                "extracted_text": content_str,
                "status": "SUCCESS"
            }

        # Fallback generic read
        else:
            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    text_content = f.read(3000)
                return {
                    "filename": filename,
                    "file_type": f"{ext.upper()} File",
                    "extracted_text": f"File {filename}:\n{text_content}",
                    "status": "SUCCESS"
                }
            except Exception as e:
                return {"filename": filename, "extracted_text": f"Read error: {e}", "status": "ERROR"}
