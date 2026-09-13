import os
import pandas as pd
from loguru import logger
import pdfplumber
import docx
import pytesseract
from PIL import Image

# M-01 / DoS Protection: Decompression limits and resource caps
Image.MAX_IMAGE_PIXELS = 10_000_000  # Max 10 Megapixels to prevent PIL decompression bombs
MAX_PDF_PAGES = 50
MAX_SPREADSHEET_ROWS = 5000
MAX_DOCX_PARAGRAPHS = 2000

def parse_pdf(file_path: str) -> str:
    """Extracts text from a PDF file up to MAX_PDF_PAGES."""
    text_content = []
    try:
        with pdfplumber.open(file_path) as pdf:
            total_pages = len(pdf.pages)
            pages_to_process = pdf.pages[:MAX_PDF_PAGES]
            for page in pages_to_process:
                text = page.extract_text()
                if text:
                    text_content.append(text)
            if total_pages > MAX_PDF_PAGES:
                text_content.append(f"\n[Notice: Truncated at {MAX_PDF_PAGES} of {total_pages} total pages.]")
        return "\n".join(text_content)
    except Exception as e:
        logger.error(f"Error parsing PDF {file_path}: {e}")
        return f"Error extracting text from PDF: {str(e)}"

def parse_docx(file_path: str) -> str:
    """Extracts text from a DOCX file up to MAX_DOCX_PARAGRAPHS."""
    try:
        doc = docx.Document(file_path)
        paragraphs = doc.paragraphs[:MAX_DOCX_PARAGRAPHS]
        text = "\n".join([p.text for p in paragraphs if p.text.strip()])
        if len(doc.paragraphs) > MAX_DOCX_PARAGRAPHS:
            text += f"\n[Notice: Truncated at {MAX_DOCX_PARAGRAPHS} paragraphs.]"
        return text
    except Exception as e:
        logger.error(f"Error parsing DOCX {file_path}: {e}")
        return f"Error extracting text from DOCX: {str(e)}"

def parse_csv(file_path: str) -> str:
    """Extracts text from a CSV file up to MAX_SPREADSHEET_ROWS."""
    try:
        df = pd.read_csv(file_path, nrows=MAX_SPREADSHEET_ROWS)
        return df.to_string(index=False)
    except Exception as e:
        logger.error(f"Error parsing CSV {file_path}: {e}")
        return f"Error extracting text from CSV: {str(e)}"

def parse_excel(file_path: str) -> str:
    """Extracts text from an Excel file up to MAX_SPREADSHEET_ROWS."""
    try:
        df = pd.read_excel(file_path, nrows=MAX_SPREADSHEET_ROWS)
        return df.to_string(index=False)
    except Exception as e:
        logger.error(f"Error parsing Excel {file_path}: {e}")
        return f"Error extracting text from Excel: {str(e)}"

def parse_image(file_path: str) -> str:
    """Extracts text from an image with decompression bomb protection."""
    try:
        with Image.open(file_path) as img:
            if Image.MAX_IMAGE_PIXELS is not None and (img.width * img.height) > Image.MAX_IMAGE_PIXELS:
                return "Error: Image dimensions exceed safe parsing limits (10MP)."
            text = pytesseract.image_to_string(img)
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
    elif ext in (".xlsx", ".xls"):
        return parse_excel(file_path)
    elif ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp"]:
        return parse_image(file_path)
    elif ext in [".txt", ".md", ".json"]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    else:
        return f"Unsupported file type: {ext}"
