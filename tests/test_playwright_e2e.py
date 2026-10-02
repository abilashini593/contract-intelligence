import os
import time
import socket
import threading
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer
import pytest
from playwright.sync_api import sync_playwright

class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("", 0))
    port = s.getsockname()[1]
    s.close()
    return port

@pytest.fixture(scope="module")
def frontend_server():
    dist_dir = os.path.abspath("frontend/dist")
    port = get_free_port()

    class DistHandler(QuietHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=dist_dir, **kwargs)

    server = TCPServer(("127.0.0.1", port), DistHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    time.sleep(0.5)

    yield f"http://127.0.0.1:{port}"

    server.shutdown()
    server.server_close()

SAMPLE_CONTRACT_DETAIL = """{
  "id": 1,
  "title": "Master Services Agreement (Apex & Meridian)",
  "description": "Initial MSA",
  "created_at": "2026-03-01T10:00:00",
  "updated_at": "2026-03-01T10:00:00",
  "versions": [
    {
      "id": 10,
      "contract_id": 1,
      "version_number": 1,
      "filename": "msa.pdf",
      "file_type": "pdf",
      "is_active": true,
      "parties": [
        {
          "id": 101,
          "version_id": 10,
          "name": "Apex Cloud Solutions Inc.",
          "role": "Vendor",
          "effective_date": "2026-03-01",
          "jurisdiction": "Delaware",
          "status": "APPROVED",
          "is_stale": false,
          "source_section": "Preamble",
          "source_page": 1,
          "source_quote": "Apex Cloud Solutions Inc. ('Vendor')",
          "certainty": "CONFIRMED",
          "confidence_score": 1.0
        }
      ],
      "clauses": [
        {
          "id": 102,
          "version_id": 10,
          "clause_type": "RENEWAL",
          "title": "Automatic Renewal Notice",
          "summary": "Renews automatically unless 60 days written notice is given.",
          "expiry_date": "2028-02-29",
          "notice_period_days": 60,
          "status": "PENDING",
          "is_stale": false,
          "source_section": "Section 2.1",
          "source_quote": "at least sixty (60) days prior to expiration",
          "certainty": "CONFIRMED",
          "confidence_score": 1.0
        }
      ],
      "obligations": [
        {
          "id": 103,
          "version_id": 10,
          "title": "Annual SOC 2 Audit",
          "description": "Deliver SOC 2 Type II compliance audit report.",
          "responsible_party": "Vendor",
          "due_date": "2026-09-30",
          "frequency": "One-time",
          "status": "APPROVED",
          "is_stale": false,
          "source_section": "Section 4.1",
          "source_quote": "Vendor shall provide Client with an updated SOC 2 report",
          "certainty": "CONFIRMED",
          "confidence_score": 1.0
        }
      ],
      "unclear_terms": [
        {
          "id": 104,
          "version_id": 10,
          "term_title": "Disaster Recovery Benchmark",
          "clause_reference": "Section 6.1",
          "issue_type": "AMBIGUITY",
          "description": "Uses vague industry benchmarks without concrete RTO/RPO limits.",
          "status": "PENDING",
          "is_stale": false,
          "source_section": "Section 6.1",
          "source_quote": "adhering to commercially standard practices",
          "certainty": "UNCERTAIN",
          "confidence_score": 0.5,
          "clarification_questions": [
            {
              "id": 1,
              "question": "What specific recovery time objective (RTO) is required?",
              "suggested_action": "Mandate RTO <= 4 hours."
            }
          ]
        }
      ]
    }
  ]
}"""

SAMPLE_SUMMARY = """{
  "contract_id": 1,
  "contract_title": "Master Services Agreement (Apex & Meridian)",
  "version_number": 1,
  "version_id": 10,
  "effective_date": "2026-03-01",
  "expiry_date": "2028-02-29",
  "renewal_summary": "Auto-renewal with 60 days notice",
  "termination_summary": "90 days for convenience",
  "approved_parties": [
    {
      "id": 101,
      "version_id": 10,
      "name": "Apex Cloud Solutions Inc.",
      "role": "Vendor",
      "effective_date": "2026-03-01",
      "jurisdiction": "Delaware",
      "status": "APPROVED",
      "is_stale": false,
      "source_section": "Preamble",
      "source_page": 1,
      "source_quote": "Apex Cloud Solutions Inc. ('Vendor')",
      "certainty": "CONFIRMED",
      "confidence_score": 1.0
    }
  ],
  "approved_clauses": [],
  "approved_obligations": [
    {
      "id": 103,
      "version_id": 10,
      "title": "Annual SOC 2 Audit",
      "description": "Deliver SOC 2 Type II compliance audit report.",
      "responsible_party": "Vendor",
      "due_date": "2026-09-30",
      "frequency": "One-time",
      "status": "APPROVED",
      "is_stale": false,
      "source_section": "Section 4.1",
      "source_quote": "Vendor shall provide Client with an updated SOC 2 report",
      "certainty": "CONFIRMED",
      "confidence_score": 1.0
    }
  ],
  "calculated_reminders": [
    {
      "id": 1,
      "version_id": 10,
      "title": "Obligation Due (30d): Annual SOC 2 Audit",
      "category": "OBLIGATION_DEADLINE",
      "target_date": "2026-09-30",
      "reminder_date": "2026-08-31",
      "days_before": 30,
      "responsible_party": "Vendor",
      "description": "Annual SOC 2 report delivery",
      "urgency": "LOW",
      "is_dismissed": false,
      "created_at": "2026-03-01T10:00:00"
    }
  ],
  "flagged_unclear_terms": [],
  "policy_checks_count": 0,
  "total_approved_items": 2,
  "total_pending_items": 2,
  "total_stale_items": 0,
  "disclaimer": "DISCLAIMER: This document is an information-management summary generated by an automated information-management system. It is provided solely for administrative and organizational tracking purposes. It does not constitute legal advice, a formal legal opinion, or a recommendation. Users should consult qualified legal counsel for any legal interpretation or decision-making.",
  "generated_at": "2026-03-01T10:05:00",
  "markdown_content": "# Reviewed Summary\\nDISCLAIMER: Administrative Information Management"
}"""

def test_frontend_ui_and_legal_disclaimers(frontend_server):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        page.route("**/api/contracts", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body="""[
              {
                "id": 1,
                "title": "Master Services Agreement (Apex & Meridian)",
                "description": "Initial MSA",
                "created_at": "2026-03-01T10:00:00",
                "updated_at": "2026-03-01T10:00:00",
                "latest_version": 1,
                "parties_count": 2,
                "clauses_count": 4,
                "obligations_count": 3,
                "unclear_terms_count": 1,
                "stale_items_count": 0
              }
            ]"""
        ))

        page.route("**/api/contracts/1", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=SAMPLE_CONTRACT_DETAIL
        ))

        page.route("**/api/contracts/1/summary*", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=SAMPLE_SUMMARY
        ))

        page.goto(frontend_server)
        page.wait_for_load_state("networkidle")

        # 1. Assert Legal Disclaimer Banner
        assert page.locator("text=ADMINISTRATIVE NOTICE").first.is_visible()
        page_text = page.locator("body").inner_text()
        assert "not provide legal advice" in page_text
        assert "Deterministic Rule Engine Active" in page_text
        assert "ContractIntelligence" in page_text
        assert "ADMIN TOOL" in page_text.upper()

        # 2. Click contract card to navigate to contract detail
        card = page.locator("text=Master Services Agreement (Apex & Meridian)").first
        card.click()
        page.wait_for_timeout(500)

        # 3. Assert Parties Tab is active and shows Apex Cloud Solutions Inc.
        assert page.locator("text=Apex Cloud Solutions Inc.").first.is_visible()
        assert page.locator("text=Vendor").first.is_visible()

        # 4. Open Source Citation Modal
        cite_btn = page.locator("button:has-text('Preamble')").first
        cite_btn.click()
        page.wait_for_timeout(300)
        assert page.locator("text=Source Citation & Document Lineage").is_visible()
        assert page.locator("text=Verbatim Excerpt from Uploaded Document").is_visible()

        # Close citation modal
        page.locator("button:has-text('Close')").first.click()
        page.wait_for_timeout(300)

        # 5. Switch to Clauses Tab
        clauses_tab = page.locator("button:has-text('Clauses')").first
        clauses_tab.click()
        page.wait_for_timeout(300)
        assert page.locator("text=Automatic Renewal Notice").first.is_visible()
        assert page.locator("text=60 days").first.is_visible()

        # 6. Switch to Obligations Tab
        obs_tab = page.locator("button:has-text('Obligations & Deadlines')").first
        obs_tab.click()
        page.wait_for_timeout(300)
        assert page.locator("text=Annual SOC 2 Audit").is_visible()
        assert page.locator("text=2026-09-30").is_visible()

        # 7. Switch to Ambiguities & Policy Conflicts Tab
        unclear_tab = page.locator("button:has-text('Ambiguities & Policy')").first
        unclear_tab.click()
        page.wait_for_timeout(300)
        assert page.locator("text=Disaster Recovery Benchmark").is_visible()
        assert page.locator("text=What specific recovery time objective (RTO) is required?").is_visible()

        # 8. Switch to Reviewed Summary Tab
        summary_tab = page.locator("button:has-text('Reviewed Contract Summary')").first
        summary_tab.click()
        page.wait_for_timeout(500)
        assert page.locator("text=Reviewed Contract Summary: Master Services Agreement").is_visible()
        assert page.locator("text=Administrative Information Management Disclaimer").is_visible()
        assert page.locator("text=Copy Markdown").is_visible()
        assert page.locator("text=Browser Print / Save PDF").is_visible()

        browser.close()
