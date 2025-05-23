import pdfplumber
from docx import Document
import os

def extract_text(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            return "\n".join(
                page.extract_text() for page in pdf.pages if page.extract_text()
            ).strip()
    
    elif ext == ".docx":
        doc = Document(file_path)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs).strip()

    else:
        raise ValueError("Formato de archivo no soportado. Usá PDF o DOCX.")
