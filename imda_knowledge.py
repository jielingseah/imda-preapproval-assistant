"""
IMDA Pre-Approval Knowledge Retrieval & Gemini Multi-Turn RAG Engine.
Centralizes official portal URLs, model constants, and live guide scrapers.
"""

import requests
import re
from google import genai
from google.genai import types

# Centralized System Constants
MODEL_NAME = "gemini-3.8-flash"
BASE_URL = "https://preapproval-guide.imda.gov.sg"
CATEGORY_DIRECTORY_URL = (
    f"{BASE_URL}/pre-approval-guide/stage-1-vendor-self-assessment/identify-suitable-solution-category.md"
)
STAGE_2_GUIDE_URL = (
    f"{BASE_URL}/pre-approval-guide/stage-2-vendor-application"
)
VMP_PORTAL_URL = "https://services2-stg.imda.gov.sg/VMP/"

CACHE_TTL_SECONDS = 3600

def fetch_markdown_document(url: str) -> str:
    """Safely retrieves markdown text content from an HTTP URL."""
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return ""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception:
        return ""

def query_live_guide_rag(
    client: genai.Client,
    user_query: str,
    chat_history: list[dict],
    user_assessment: dict,
    selected_category: str | None = None,
    model_name: str = MODEL_NAME
) -> str:
    """
    Executes a grounded multi-turn RAG generation using live guide content
    and strict XML prompt boundaries.
    """
    stage_1_text = fetch_markdown_document(
        f"{BASE_URL}/pre-approval-guide/stage-1-vendor-self-assessment.md"
    )
    stage_2_text = fetch_markdown_document(
        f"{BASE_URL}/pre-approval-guide/stage-2-vendor-application.md"
    )
    
    reference_context = (
        f"--- STAGE 1 GUIDE ---\n{stage_1_text[:4000]}\n\n"
        f"--- STAGE 2 GUIDE ---\n{stage_2_text[:4000]}"
    )

    system_instruction = (
        "You are the official IMDA Pre-Approval AI Copilot under the SMEs Go Digital programme. "
        "Answer questions accurately, grounded in the official guide context provided. "
        "Maintain a helpful, professional tone. If the user asks about unmet criteria, suggest practical "
        "remediation steps or alternative pathways outlined by IMDA policy."
    )

    history_formatted = "\n".join(
        [f"{msg['role'].upper()}: {msg['content']}" for msg in chat_history[-6:]]
    )

    prompt = f"""
<context>
{reference_context}
</context>

<applicant_state>
Target Category: {selected_category or "Not yet selected"}
Assessment Responses: {user_assessment}
</applicant_state>

<conversation_history>
{history_formatted}
</conversation_history>

<user_query>
{user_query}
</user_query>
"""

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2
            )
        )
        return response.text
    except Exception as e:
        return f"I apologize, but I encountered an error while consulting the official guide: {str(e)}"
