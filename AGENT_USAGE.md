# Agent Usage & AI Collaboration Log

## 1. AI Tools & Models Used
- **Primary Intelligence Model:** Google Gemini API (`gemini-2.5-flash` / `gemini-1.5-pro`)
- **Primary Agent Framework:** Custom FastAPI AI Ingestion & Analysis Pipeline
- **Development Partner:** Gemini AI Assistant (Architecture, Debugging, Validation)

## 2. Delegation of Work
- **Automated Tasks (Delegated to LLM Agent):**
  - Extracting parties, effective dates, governing jurisdiction, and initial clause breakdown from unstructured `.txt`, `.docx`, and `.pdf` files.
  - Cross-referencing extracted terms against the uploaded Organizational Policy document.
  - Drafting clear, non-punitive negotiation clarification questions for policy non-compliance risks.
- **Deterministic Work (Excluded from LLM Automation):**
  - **Date Arithmetic Engine:** All advance reminder dates (90d, 60d, 30d, 14d, 7d, 1d) and recurring payment/invoicing cycles are computed strictly using standard Python `datetime` arithmetic to ensure 100% mathematical accuracy without LLM date hallucination.

## 3. Representative Prompts
- **Ingestion & Extraction:**
  > *"Extract structured JSON containing parties, effective date, clause summary, and obligations from the attached contract document."*
- **Policy Cross-Referencing:**
  > *"Compare the extracted SLA response time (2 hours) and status update frequency (4 hours) against the Standard Vendor Policy thresholds. Highlight discrepancies and formulate clarification questions for vendor negotiation."*

## 4. Agent Errors, Rejected Suggestions & Course Corrections
- **Attempted LLM Date Calculation:**
  - *Initial Behavior:* The initial prototype attempted to let the LLM estimate reminder lead times directly from contract text.
  - *Correction:* Rejected LLM date inference in favor of a dedicated Python deterministic date calculation module that takes extracted anchor dates and computes exact targets programmatically.
- **Vague Policy Questions:**
  - *Initial Behavior:* AI generated generic questions like *"Is this SLA compliant?"*
  - *Correction:* Prompt engineering was tightened to mandate specific counter-proposals (e.g., explicitly asking if the provider agrees to amend the SLA from 2 hours to 1 hour to match Policy v2.1).

## 5. Output Verification Process
- **Human-in-the-Loop Review:** All AI-extracted clauses and policy flags remain in a `PENDING REVIEW` state until explicitly confirmed or edited by a user in the UI.
- **Test Matrix Validation:** Verified extraction accuracy across `.txt`, `.docx`, and `.pdf` files using `sample_contract.pdf` and verified all 11 calculated reminders against manual date arithmetic.