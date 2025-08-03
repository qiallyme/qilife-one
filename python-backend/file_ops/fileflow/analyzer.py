import os
from datetime import datetime
from PIL import Image
import pytesseract
from filetype import guess

# PDF reading
from pdfminer.high_level import extract_text

def extract_text_from_image(path):
    try:
        return pytesseract.image_to_string(Image.open(path))
    except Exception as e:
        print(f"⚠️ OCR failed on image: {e}")
        return ""

def extract_text_from_pdf(path):
    try:
        return extract_text(path)
    except Exception as e:
        print(f"⚠️ PDF text extraction failed: {e}")
        return ""

def analyze_file(filepath):
    filename = os.path.basename(filepath)
    timestamp = os.path.getmtime(filepath)
    ext = os.path.splitext(filepath)[1].lower()

    # Filetype-based switch
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp"]:
        text = extract_text_from_image(filepath)
    elif ext == ".pdf":
        text = extract_text_from_pdf(filepath)
    else:
        text = ""  # For now — fallback to future modes

    return {
        "text": text,
        "timestamp": datetime.fromtimestamp(timestamp).strftime("%Y%m%d_%H%M%S"),
        "original_filename": filename
    }
