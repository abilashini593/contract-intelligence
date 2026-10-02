import pymupdf as fitz
from typing import Dict, List, Tuple

class PDFParsingError(Exception):
    pass

def extract_text_from_pdf(file_bytes: bytes) -> Tuple[str, List[Dict[str, any]]]:
    """
    Extracts text from a text-based PDF using PyMuPDF (fitz).
    Returns:
        - formatted_text: Full text with [Page X] headers.
        - page_data: List of dicts with page number, character start/end offsets, and text.
    Raises:
        - PDFParsingError: If file is corrupted or is a scanned image without selectable text.
    """
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
    except Exception as e:
        raise PDFParsingError(f"Could not open PDF file. It may be corrupt or encrypted: {str(e)}")

    if len(doc) == 0:
        raise PDFParsingError("The uploaded PDF is empty.")

    page_data = []
    full_text_parts = []
    total_text_length = 0

    for page_idx in range(len(doc)):
        page_num = page_idx + 1
        page = doc[page_idx]
        text = page.get_text("text").strip()

        if text:
            page_header = f"--- [Page {page_num}] ---\n"
            start_offset = total_text_length
            full_text_parts.append(page_header + text + "\n\n")
            total_text_length += len(page_header) + len(text) + 2
            page_data.append({
                "page": page_num,
                "text": text,
                "char_start": start_offset,
                "char_end": total_text_length
            })

    doc.close()

    formatted_text = "".join(full_text_parts).strip()

    # Verify that text was actually extracted (scanned image check)
    if not formatted_text or total_text_length < 20:
        raise PDFParsingError(
            "No extractable text found in this PDF. This document appears to be a scanned image or empty. "
            "Per system specifications, OCR is not supported. Please upload a text-based PDF or paste text directly."
        )

    return formatted_text, page_data
