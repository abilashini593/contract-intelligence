import re
from typing import Dict, List, Tuple

class TextParsingError(Exception):
    pass

def extract_text_from_raw(raw_input: str) -> Tuple[str, List[Dict[str, any]]]:
    """
    Validates and normalizes raw text input or plain .txt files.
    """
    if not raw_input or not raw_input.strip():
        raise TextParsingError("The text input is empty.")

    cleaned_text = raw_input.strip()
    if len(cleaned_text) < 20:
        raise TextParsingError("The text content is too short to be analyzed as a contract or policy.")

    # Split into sections if headings are present
    lines = cleaned_text.splitlines()
    sections = []
    current_section = "General"

    for line in lines:
        line_s = line.strip()
        if not line_s:
            continue
        # Detect common section patterns like 'Section 1.', '1. Term', 'ARTICLE I'
        if re.match(r'^(Section|Article|\d+\.|\b[A-Z\s]{4,}\b:)', line_s, re.IGNORECASE) and len(line_s) < 80:
            current_section = line_s
            sections.append({"section": line_s, "type": "heading"})
        else:
            sections.append({"section": current_section, "text": line_s, "type": "body"})

    return cleaned_text, sections
