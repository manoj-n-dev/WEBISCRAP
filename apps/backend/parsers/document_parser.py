import os
import pandas as pd
from loguru import logger
import pdfplumber
import docx
import pytesseract
from PIL import Image

def parse_pdf(file_path: str) -> str:
    """Extracts text from a PDF file."""
    text_content = []
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        return "\n".join(text_content)
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        return f"Error extracting text from PDF: {str(e)}"

def parse_docx(file_path: str) -> str:
    """Extracts text from a DOCX file."""
    try:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {e}")
        return f"Error extracting text from DOCX: {str(e)}"

def parse_csv(file_path: str) -> str:
    """Extracts text from a CSV file by converting to string representation."""
    try:
        df = pd.read_csv(file_path)
        return df.to_string(index=False)
    except Exception as e:
        logger.error(f"Error parsing CSV {file_path}: {e}")
        return f"Error extracting text from CSV: {str(e)}"

def parse_image(file_path: str) -> str:
    """Extracts text from an image using Tesseract OCR."""
    try:
        # Note: Requires Tesseract OCR installed on the system
        text = pytesseract.image_to_string(Image.open(file_path))
        return text
    except Exception as e:
        logger.error(f"Error parsing Image {file_path}: {e}")
        return f"Error extracting text from Image: {str(e)}. Ensure Tesseract is installed on the system."

def extract_text_from_file(file_path: str) -> str:
    """Main routing function to parse any supported file."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        return parse_pdf(file_path)
    elif ext == ".docx":
        return parse_docx(file_path)
    elif ext == ".csv":
        return parse_csv(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        return parse_image(file_path)
    elif ext in [".txt", ".md", ".json"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        return f"Unsupported file type: {ext}"
