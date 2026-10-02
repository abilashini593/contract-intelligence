# Contract Intelligence & Administrative Information Management Platform

A production-grade, full-stack contract intelligence and deadline-management system built with **FastAPI**, **PostgreSQL**, **Google Gemini API**, **PyMuPDF**, **python-docx**, and **React + Vite**.

> [!IMPORTANT]
> **LEGAL NOTICE & INFORMATION MANAGEMENT DISCLAIMER**
> This application strictly presents itself as an **information-management and administrative tracking tool**, **not as legal advice, formal legal opinions, or recommendations**. It is designed solely to catalog contractual terms, calculate deterministic milestone deadlines, and track obligations across contract revisions. Qualified legal counsel should always be consulted for legal interpretations.

---

## Key Features

1. **Multi-Format Document Parsing (No OCR)**:
   - Supports text-based **PDF** (via PyMuPDF / fitz with per-page tracking).
   - Supports **DOCX** (via python-docx with paragraph and heading extraction).
   - Supports **pasted raw text** and `.txt` files.
   - Strictly validates file formats and warns users if a scanned image without selectable text is uploaded.
2. **Gemini AI Structured Extraction Engine**:
   - Uses the official Google Gemini SDK (`google-genai`) with strict Pydantic JSON schema validation.
   - Extracts formal **contract parties**, jurisdiction, and effective dates.
   - Extracts **expiry, renewal, termination, and notice clauses**.
   - Extracts **actionable obligations, deadlines, and responsible parties**.
   - Identifies **ambiguous, conflicting, or missing terms**.
   - **Cross-References Organizational Policies**: If an optional organizational policy document is uploaded, flags any contract terms that contradict policy standards under `issue_type="POLICY_CONFLICT"`.
   - **Exact Source Citations**: Every extracted item includes exact `source_page`, `source_section`, and `source_quote` (verbatim text).
   - **Distinguishes Confirmed from Uncertain**: Categorizes items as `CONFIRMED` vs. `UNCERTAIN` with confidence scores and rationales.
   - **Generates Targeted Clarification Questions** for ambiguous clauses.
3. **Deterministic Backend Date & Deadline Engine (Zero AI for Dates)**:
   - All reminder dates and notice cutoffs are calculated using deterministic Python date arithmetic (`datetime`, `dateutil`), ensuring 100% mathematical accuracy.
   - Calculates **Renewal Notice Cutoffs** (`expiry_date - notice_period_days`) with advance reminders at 30, 14, 7, and 0 days prior.
   - Calculates **Contract Expiry Reminders** at 90, 60, 30, 14, and 7 days before expiry.
   - Calculates **Obligation Deadlines** with advance warning schedules.
   - Handles **Recurring Obligations** (monthly, quarterly, annual cadences).
   - Computes live urgency states: `OVERDUE`, `HIGH (<= 7 days)`, `MEDIUM (<= 30 days)`, and `LOW`.
4. **Contract Versioning & Stale Item Detection**:
   - Preserves contract versions (`v1`, `v2`, etc.) and user corrections.
   - When a new revision is uploaded, compares against previously approved items.
   - Marks altered clauses or deadlines as **`STALE (RE-REVIEW NEEDED)`** with a human-readable diff explanation.
5. **Interactive Review & Corrections Workflow**:
   - Edit, approve, or reject extracted items with persistence in PostgreSQL.
   - Answer clarification questions directly in the interface.
6. **Reviewed Contract Summary**:
   - Generates an executive summary of confirmed metadata and approved items.
   - One-click **Markdown Export**, **Download .md**, and **Browser Print / PDF saving** (`window.print()`).
   - Prominently embeds the required information-management disclaimer.

---

## Tech Stack

| Layer | Technology | Details |
|---|---|---|
| **Frontend** | React 18, Vite, JavaScript, Tailwind CSS | Modular components, Lucide icons, responsive design |
| **Backend** | Python 3.11, FastAPI, Uvicorn | Async REST APIs, Pydantic v2 schemas |
| **Database** | PostgreSQL | SQLAlchemy ORM, relational schema with cascading versioning |
| **AI Integration** | Google Gemini API (`gemini-2.5-flash`) | Structured JSON output via `google-genai` SDK |
| **Document Parsers** | PyMuPDF (fitz), python-docx | Pure text & structure extraction (No OCR) |
| **Testing** | Pytest + Playwright | Unit tests, deterministic date tests, API tests, E2E browser tests |
| **Deployment** | Docker & Docker Compose | Multi-container setup (`db`, `backend`, `frontend`) |

---

## Project Structure

```
contract-intelligence/
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI entrypoint, CORS, lifespan, exception handlers
│   │   ├── config.py                   # App configuration and database URL normalization
│   │   ├── database.py                 # SQLAlchemy engine, session maker, init_db
│   │   ├── models/                     # Relational database models
│   │   │   ├── contract.py             # Contract, ContractVersion, PolicyDocument
│   │   │   ├── extracted_item.py       # ExtractedParty, ExtractedClause, ExtractedObligation, UnclearTerm
│   │   │   └── reminder.py             # CalculatedReminder
│   │   ├── schemas/                    # Pydantic schemas (Request/Response & Gemini Structured JSON)
│   │   │   ├── contract.py
│   │   │   ├── extraction.py
│   │   │   ├── reminder.py
│   │   │   └── summary.py
│   │   ├── parsers/                    # Deterministic document parsing (No OCR)
│   │   │   ├── pdf_parser.py           # PyMuPDF text & page extractor
│   │   │   ├── docx_parser.py          # python-docx paragraph/heading extractor
│   │   │   └── text_parser.py          # Plain text parser
│   │   ├── services/
│   │   │   ├── gemini_service.py       # Gemini API client with structured JSON output
│   │   │   ├── reminder_service.py     # Deterministic date calculation engine (Python date math)
│   │   │   ├── stale_service.py        # Version comparison & stale item detection
│   │   │   └── summary_service.py      # Reviewed contract summary generator
│   │   └── api/                        # REST API routers
│   │       ├── contracts.py            # Upload, versions, retrieval
│   │       ├── items.py                # Item status (approve, reject, edit)
│   │       ├── reminders.py            # Upcoming obligations and renewal deadlines
│   │       └── summary.py              # Reviewed summary report
│   ├── tests/                          # Automated Pytest suite
│   │   ├── test_parsers.py
│   │   ├── test_reminder_calculations.py
│   │   ├── test_stale_detection.py
│   │   ├── test_summary_service.py
│   │   └── test_contracts_api.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── api/client.js               # Centralized Axios API client
│   │   ├── components/                 # Reusable React components
│   │   │   ├── Navbar.jsx              # Header with Disclaimer & API key config
│   │   │   ├── UploadModal.jsx         # Upload contract & optional policy modal
│   │   │   ├── ContractsList.jsx       # Contract dashboard & search
│   │   │   ├── ContractDetailView.jsx  # Main contract detail & tab navigator
│   │   │   ├── ItemCard.jsx            # Card with status, certainty, and actions
│   │   │   ├── ItemEditModal.jsx       # Item editor modal
│   │   │   ├── SourceCitationModal.jsx # Verbatim source citation modal
│   │   │   ├── StaleAlertBanner.jsx    # Stale items detection alert
│   │   │   ├── DeadlinesDashboard.jsx  # Deterministic reminders & deadlines view
│   │   │   └── ContractSummaryView.jsx # Reviewed summary view & print export
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   ├── nginx.conf
│   └── Dockerfile
├── tests/
│   └── test_playwright_e2e.py          # Playwright end-to-end browser test suite
├── sample_data/                        # Sample contracts and policies for immediate testing
│   ├── master_services_agreement.txt   # Complete Master Services Agreement
│   ├── organizational_security_policy.txt # Organizational compliance policy
│   └── amendment_v2.txt                # Version 2 amendment with altered terms
├── docker-compose.yml
├── pytest.ini
├── .gitignore
├── .env.example
└── README.md
```

---

## Environment Variables

Copy `.env.example` to `.env` or set environment variables:

```bash
# PostgreSQL Database Settings
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/contract_intelligence
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=contract_intelligence
POSTGRES_PORT=5432

# Google Gemini API Key (Required for AI Extraction)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash

# Services Configuration
BACKEND_PORT=8000
FRONTEND_PORT=5173
```

> [!TIP]
> You can also supply the Gemini API Key directly in the frontend UI via the Key icon in the navigation bar. Keys provided this way are stored in `sessionStorage` and sent securely via the `X-Gemini-API-Key` request header.

---

## Running with Docker (Recommended)

To launch the complete application with PostgreSQL, FastAPI, and React in containers:

```bash
# 1. Provide your Gemini API key in .env
echo "GEMINI_API_KEY=your_key_here" > .env

# 2. Build and start containers
docker-compose up --build
```

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Interactive OpenAPI Docs**: http://localhost:8000/docs
- **PostgreSQL**: `localhost:5432`

---

## Running Locally

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL running locally or in Docker

### 1. Database Setup
Ensure PostgreSQL is running and the database exists:
```sql
CREATE DATABASE contract_intelligence;
```

### 2. Backend Setup
```bash
# From project root
cd backend

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate   # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DATABASE_URL and GEMINI_API_KEY

# Start backend server
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Frontend Setup
```bash
# In a new terminal, from project root
cd frontend

# Install npm dependencies
npm install

# Start Vite dev server
npm run dev
```

Visit **http://localhost:5173** to use the application.

---

## Running Automated Tests

### 1. Backend Pytest Suite
Runs all unit tests for parsers, deterministic date calculations, stale item detection, summary generation, and REST APIs:

```bash
python -m pytest backend/tests -v
```

### 2. Playwright End-to-End Tests
Executes headless browser tests validating the full user workflow, tab navigation, citation modal popups, and legal disclaimers:

```bash
python -m pytest tests/test_playwright_e2e.py -v
```

### 3. Run All Tests Together
```bash
python -m pytest backend/tests tests/test_playwright_e2e.py -v
```

---

## Sample Contracts for Testing

Pre-configured sample documents are available in `sample_data/`:
1. `sample_data/master_services_agreement.txt`:
   - Parties: *Apex Cloud Solutions Inc.* (Vendor) and *Meridian Financial Corp.* (Client).
   - Term: 2 years (expiring Feb 29, 2028).
   - Renewal: Auto-renewal with 60 days written notice.
   - Obligations: Annual SOC 2 Type II audit, monthly invoicing, payment in 30 days.
   - Unclear Terms: Vague disaster recovery benchmarks without explicit RTO/RPO.
2. `sample_data/organizational_security_policy.txt`:
   - Meridian Financial Corp.'s corporate security policy.
   - Stipulates 24-hour breach notification mandate (conflicts with contract's 72-hour clause).
   - Mandates renewal notice periods must not exceed 30 days (conflicts with contract's 60 days).
3. `sample_data/amendment_v2.txt`:
   - Amendment No. 1 (Version 2) modifying renewal notice to 30 days, extending term to Dec 31, 2028, and altering payment terms to 45 days.
   - Uploading this as Version 2 triggers the **Stale Items Detection Engine** and demonstrates version revision diffs!
