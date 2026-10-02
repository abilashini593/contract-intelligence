import json
import logging
from typing import Optional
from app.config import settings
from app.schemas.extraction import ContractAnalysisAIOutput

logger = logging.getLogger(__name__)

class GeminiServiceError(Exception):
    pass

class GeminiAPIKeyMissingError(GeminiServiceError):
    pass

def analyze_contract_with_gemini(
    contract_text: str,
    policy_text: Optional[str] = None,
    api_key: Optional[str] = None
) -> ContractAnalysisAIOutput:
    """
    Calls the Google Gemini API using google-genai SDK to analyze contract text
    and optional policy document text with strict structured JSON schema.
    """
    effective_api_key = api_key or settings.GEMINI_API_KEY
    if not effective_api_key or effective_api_key.strip() == "" or "your_gemini_api_key" in effective_api_key:
        raise GeminiAPIKeyMissingError(
            "GEMINI_API_KEY is not configured. Please provide a valid Gemini API key in backend/.env "
            "or pass it via the X-Gemini-API-Key request header."
        )

    try:
        from google import genai
        from google.genai import types
    except ImportError:
        raise GeminiServiceError("The google-genai library is not installed in the backend environment.")

    client = genai.Client(api_key=effective_api_key)

    system_instruction = (
        "You are an objective legal contract analysis and information-management assistant. "
        "Your task is to parse, extract, and structure contract data for administrative tracking. "
        "You DO NOT provide legal advice or legal opinions. You extract factual stipulations, "
        "clauses, obligations, deadlines, and cite the exact source text from the document. "
        "Strictly separate confirmed facts from ambiguous or uncertain interpretations.\n\n"
        "Guidelines:\n"
        "1. Identify all formal parties (name, role, jurisdiction, effective date).\n"
        "2. Extract expiry, renewal, termination, and notice clauses.\n"
        "3. Extract all actionable obligations, their deadlines (YYYY-MM-DD or frequency), and responsible parties.\n"
        "4. Identify any unclear, conflicting, or missing terms (e.g. undefined terms, contradictory notice windows).\n"
        "5. If an Organizational Policy document is provided, cross-check the contract against the policy document "
        "and flag any clauses that conflict with or violate the organization's policy under issue_type='POLICY_CONFLICT'.\n"
        "6. Source Citations: For EVERY party, clause, obligation, and unclear term, provide:\n"
        "   - source_page: Page number if detectable (e.g. from '[Page X]' headers) or null.\n"
        "   - source_section: Specific section number and heading (e.g. 'Section 5.2 Termination').\n"
        "   - source_quote: Exact verbatim quote from the text.\n"
        "7. Certainty: Assign certainty='CONFIRMED' for explicitly stated terms; assign certainty='UNCERTAIN' "
        "if an interpretation is required, if dates are ambiguous, or if conflicting standards exist, and provide uncertainty_rationale.\n"
        "8. Clarification Questions: For ambiguous terms, generate targeted, professional questions to clarify intent."
    )

    user_prompt_parts = [
        "Please extract structured contract intelligence from the following document:\n\n",
        "=== CONTRACT DOCUMENT TEXT ===\n",
        contract_text,
        "\n==============================\n"
    ]

    if policy_text and policy_text.strip():
        user_prompt_parts.extend([
            "\n=== ORGANIZATIONAL POLICY DOCUMENT ===\n",
            policy_text,
            "\n======================================\n",
            "Please cross-reference the contract clauses against the Organizational Policy document above. "
            "Flag any contract terms that violate or contradict the policy as 'POLICY_CONFLICT' in unclear_terms."
        ])

    full_prompt = "".join(user_prompt_parts)

    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=full_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                response_mime_type="application/json",
                response_schema=ContractAnalysisAIOutput,
                temperature=0.1,
            ),
        )

        if not response.text:
            raise GeminiServiceError("Gemini returned an empty response.")

        # Parse and validate through Pydantic
        output_data = json.loads(response.text)
        validated_output = ContractAnalysisAIOutput.model_validate(output_data)
        return validated_output

    except json.JSONDecodeError as jde:
        logger.error(f"JSON decode failure from Gemini response: {jde}")
        raise GeminiServiceError(f"Failed to parse structured JSON from Gemini response: {str(jde)}")
    except Exception as e:
        logger.error(f"Error calling Gemini API: {str(e)}", exc_info=True)
        raise GeminiServiceError(f"Gemini API analysis failed: {str(e)}")
