#!/usr/bin/env python3
"""
pdf2md.py

Lite PDF → Markdown converter for QiLife.
Uses pdfplumber for better text extraction, with a PyPDF2 fallback.
Saves output in src/qidocs/docs/QiNote™ as a .md file.
"""
import sys
from pathlib import Path

def convert_with_pdfplumber(pdf_path: Path, output_path: Path) -> bool:
    try:
        import pdfplumber
        md_lines = []
        with pdfplumber.open(pdf_path) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                md_lines.append(f"## Page {i}\n")
                text = page.extract_text() or ''
                md_lines.append(text + '\n')
        output_path.write_text(''.join(md_lines), encoding='utf-8')
        return True
    except Exception as e:
        print(f"[pdfplumber] Conversion failed: {e}")
        return False

def convert_with_pypdf2(pdf_path: Path, output_path: Path) -> bool:
    try:
        from PyPDF2 import PdfReader
        reader = PdfReader(str(pdf_path))
        md_lines = []
        for i, page in enumerate(reader.pages, start=1):
            md_lines.append(f"## Page {i}\n")
            text = page.extract_text() or ''
            md_lines.append(text + '\n')
        output_path.write_text(''.join(md_lines), encoding='utf-8')
        return True
    except Exception as e:
        print(f"[PyPDF2] Fallback failed: {e}")
        return False

def main():
    pdf_input = input("Enter the path to the PDF file: ").strip()
    pdf_path = Path(pdf_input)
    if not pdf_path.is_file():
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    # Locate project root (assumes script at src/tools/utils/fileops)
    project_root = Path(__file__).parents[4]
    output_dir = project_root / 'src' / 'qidocs' / 'docs' / 'QiNote™'
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / (pdf_path.stem + '.md')
    print(f"Converting → {output_file}")

    if convert_with_pdfplumber(pdf_path, output_file):
        print("✅ Converted via pdfplumber.")
    elif convert_with_pypdf2(pdf_path, output_file):
        print("✅ Converted via PyPDF2 fallback.")
    else:
        print("❌ All conversions failed. Install pdfplumber or PyPDF2.")
        sys.exit(1)

if __name__ == '__main__':
    main()
