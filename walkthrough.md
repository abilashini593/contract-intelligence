# Walkthrough: Contract Intelligence & Information-Management Platform

A complete, production-ready full-stack application for contract clause extraction, deterministic deadline reminders, revision stale-item detection, and reviewed contract summary generation.

> [!IMPORTANT]
> **LEGAL NOTICE: INFORMATION MANAGEMENT ONLY**
> The application strictly presents itself as an **administrative information-management tool**, **not legal advice**. Persistent notices and disclaimers are visible in the top banner, header badge, executive reports, and application footer.

---

## 1. What Was Implemented

### Backend Architecture (`FastAPI` + `PostgreSQL` + `Google Gemini API`)
- **Document Ingestion (No OCR)**:
  - `pdf_parser.py`: PyMuPDF (`fitz`) text extraction with page tracking (`[Page X]`) and scanned image detection without OCR.
  - `docx_parser.py`: `python-docx` structured parser extracting headings, paragraphs, and tables.
  - `text_parser.py`: Normalizes raw pasted text.
- **Gemini AI Structured Extraction Engine**:
  - `gemini_service.py`: Uses official `google-genai` SDK with strict JSON schema definition (`ContractAnalysisAIOutput`).
  - Identifies formal parties, formation roles, jurisdiction, and effective dates.
  - Extracts expiry, renewal, termination, and notice clauses.
  - Extracts key obligations, due dates/frequencies, and responsible parties.
  - Identifies unclear or conflicting terms and generates clarification questions.
  - **Cross-References Organizational Policies**: If an organizational policy document is uploaded, checks contract terms against policy standards and flags discrepancies as `issue_type="POLICY_CONFLICT"`.
  - **Exact Citations**: Returns `source_page`, `source_section`, and `source_quote` (verbatim text) for every extracted item.
  - **Certainty Distinction**: Classifies items as `CONFIRMED` vs. `UNCERTAIN` with confidence scores and rationales.
- **Deterministic Deadline Engine (Zero AI for Dates)**:
  - `reminder_service.py`: Pure Python date arithmetic.
  - Computes **Renewal Notice Cutoffs** (`expiry_date - notice_period_days`) and advance alerts at 30, 14, 7, and 0 days prior.
  - Computes **Contract Expiry Reminders** at 90, 60, 30, 14, and 7 days.
  - Computes **Obligation Reminders** (30, 14, 7, and 1 day prior) and recurring schedules.
  - Evaluates live urgency states: `OVERDUE`, `HIGH`, `MEDIUM`, `LOW`.
- **Versioning & Stale Item Detection**:
  - `stale_service.py`: Preserves versions (`v1`, `v2`). Compares newly uploaded revisions against previously approved items. Flags altered terms as `STALE (RE-REVIEW NEEDED)` with a human-readable diff.
- **Summary Generator**:
  - `summary_service.py`: Assembles reviewed contract summaries including only approved/edited items, calculated deadlines, and mandatory information-management disclaimers.
- **REST APIs**:
  - Upload contract, upload new version, get contract details, list contracts, delete contract.
  - Edit, approve, reject items; batch update statuses.
  - Retrieve deterministic reminders and toggle completion.
  - Export reviewed contract summary as JSON or downloadable Markdown (`.md`).

---

## 2. Test Verification & Results

All **19 automated tests** passed with 100% success rate:
- 18 Pytest unit & API tests (parsers, deterministic calculations, stale-item detection, summary generation, contract upload).
- 1 Playwright E2E browser test covering complete end-to-end user navigation, tabs, citations modal, and legal notice verification.
