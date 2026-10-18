"""
Assessment Service Layer for IMDA Pre-Approval Assistant.
Encapsulates network I/O, parsing of official markdown categories, and GenAI category matching.
"""

import streamlit as st
import requests
import re
import time
from urllib.parse import urljoin
from google import genai
from google.genai import types

from imda_knowledge import (
    MODEL_NAME,
    CATEGORY_DIRECTORY_URL,
    CACHE_TTL_SECONDS
)

def format_web_url(url: str) -> str:
    """Converts raw markdown URLs into clean browser-facing website links by stripping .md."""
    if not url:
        return ""
    if url.endswith(".md"):
        return url[:-3]
    return url

def sanitize_and_check_injection(user_input: str) -> tuple[bool, str]:
    """Sanitizes user input and flags adversarial prompt injection patterns."""
    if not user_input or not user_input.strip():
        return False, "Input cannot be empty."

    jailbreak_patterns = [
        r"ignore (all )?(previous|prior) (instructions|directions|rules)",
        r"system prompt",
        r"reveal (your )?(instructions|secret|api key|prompt)",
        r"bypass (guardrail|filter|policy|restrictions)",
        r"you are now (an unrestricted|a new|dan)",
        r"<script>",
        r"javascript:",
        r"drop table",
    ]

    for pattern in jailbreak_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False, "Input flagged by safety guardrails: contains unauthorized command sequences."

    sanitized = user_input.replace("<", "&lt;").replace(">", "&gt;")
    return True, sanitized

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_text(url: str) -> str:
    """Fetches text content from a remote URL with caching."""
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return ""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception:
        return ""

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_category_catalogue():
    """Parses and caches the official IMDA category directory markdown."""
    markdown = fetch_text(CATEGORY_DIRECTORY_URL)
    if not markdown:
        return {}

    categories = {}
    current_sector = "General"
    lines = markdown.splitlines()

    for line in lines:
        sector_match = re.search(r"Sector:\s*([^*]+)", line, flags=re.IGNORECASE)
        if sector_match:
            current_sector = sector_match.group(1).strip()

        match = re.search(r"\[([^\]]+)\]\(([^)]+\.md)\)", line)
        if not match:
            continue

        category_name = match.group(1).strip()
        relative_url = match.group(2).strip()

        if "/identify-suitable-solution-category/" not in relative_url:
            continue

        category_url = urljoin(CATEGORY_DIRECTORY_URL, relative_url)
        description = ""

        try:
            current_index = lines.index(line)
            for following_line in lines[current_index + 1:current_index + 5]:
                cleaned = following_line.strip()
                if cleaned and not cleaned.startswith("a)"):
                    description = cleaned
                    break
        except Exception:
            pass

        key = f"{current_sector}: {category_name}"
        categories[key] = {
            "sector": current_sector,
            "category": category_name,
            "url": category_url,
            "description": description
        }

    return categories

def resolve_category_info(selected_category_name: str, fallback_url: str = None) -> dict:
    """Safely retrieves category metadata with fallback matching."""
    catalogue = get_category_catalogue()
    
    if selected_category_name in catalogue:
        return catalogue[selected_category_name]
    
    if selected_category_name:
        target_lower = selected_category_name.lower().strip()
        for k, v in catalogue.items():
            if k.lower().strip() == target_lower or target_lower in k.lower():
                return v

    if fallback_url and fallback_url.startswith("http"):
        for v in catalogue.values():
            if v["url"].strip() == fallback_url.strip():
                return v

    return {
        "sector": "Identified Solution",
        "category": selected_category_name or "Official Category",
        "url": fallback_url if (fallback_url and fallback_url.startswith("http")) else CATEGORY_DIRECTORY_URL,
        "description": "Multi-functional system that streamlines operations and administration."
    }

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_category_requirements(category_url: str):
    """Fetches and parses functional requirements (Q1 to Qn) from a category guide."""
    if not category_url or not (category_url.startswith("http://") or category_url.startswith("https://")):
        return []

    markdown = fetch_text(category_url)
    if not markdown:
        return []

    questions = []
    lines = markdown.splitlines()
    total_lines = len(lines)

    for i, line in enumerate(lines):
        line_clean = line.strip()
        q_match = re.match(r"#{2,4}\s+Q(\d+)\s*(.*)", line_clean)
        if not q_match:
            continue

        q_number = q_match.group(1)
        heading = q_match.group(2).strip()
        is_mandatory = "preferred" not in heading.lower()
        heading_clean = heading.replace("**", "").replace("*", "").strip()

        question_text = ""
        for next_line in lines[i + 1:min(i + 40, total_lines)]:
            stripped = next_line.strip()
            if re.match(r"#{2,4}\s+Q\d+", stripped):
                break

            if "Main Question:" in stripped:
                question_text = stripped.split("Main Question:", 1)[1].strip()
                break
            elif "Question:" in stripped and not question_text:
                question_text = stripped.split("Question:", 1)[1].strip()
            elif stripped and not question_text and not stripped.startswith("#"):
                if not any(stripped.startswith(prefix) for prefix in ["|", "```", "<!--", "!"]):
                    question_text = stripped

        if not question_text:
            question_text = heading_clean if heading_clean else f"Requirement details for Q{q_number}"

        question_text = question_text.replace("**", "").strip()
        if question_text.endswith(":"):
            question_text = question_text[:-1]

        questions.append({
            "number": q_number,
            "heading": heading_clean,
            "question": question_text,
            "mandatory": is_mandatory
        })

    return questions

def get_gemini_client():
    """Initializes and returns the Gemini GenAI Client using secrets."""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def recommend_categories(vendor_description: str):
    """Uses Gemini to semantically match solution descriptions to official categories."""
    client = get_gemini_client()
    if client is None:
        return {"error": "GEMINI_API_KEY is not configured in Secrets."}

    catalogue = get_category_catalogue()
    catalogue_text = "\n\n".join(
        [
            f"OFFICIAL CATEGORY: {key}\nDESCRIPTION: {val['description']}\nURL: {val['url']}"
            for key, val in catalogue.items()
        ]
    )

    system_instruction = """
You are an IMDA Pre-Approval solution-category recommendation assistant.
Identify relevant official categories from the IMDA catalogue.
Return up to 3 matches.

OUTPUT FORMAT STRICTLY:
MATCH
CATEGORY: <exact official category>
WHY: <one or two sentence explanation>
"""
    user_prompt = f"<official_catalogue>\n{catalogue_text}\n</official_catalogue>\n<vendor_description>\n{vendor_description}\n</vendor_description>"

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=user_prompt,
                config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1)
            )
            return {"answer": response.text, "catalogue": catalogue}
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            return {"error": str(e)}

def parse_category_matches(answer: str, catalogue: dict):
    """Extracts structured category recommendations from LLM response text."""
    results = []
    blocks = answer.split("MATCH")

    for block in blocks:
        category_match = re.search(r"CATEGORY:\s*(.+)", block)
        why_match = re.search(r"WHY:\s*(.+)", block, flags=re.DOTALL)
        if not category_match:
            continue

        category_text = category_match.group(1).strip()
        matched_key = None

        for key in catalogue:
            if category_text.lower() == key.lower() or key.lower() in category_text.lower():
                matched_key = key
                break

        if matched_key is None:
            continue

        why = why_match.group(1).strip() if why_match else "Relevant based on provided functions."
        why = why.split("MATCH")[0].strip()

        results.append({
            "category_key": matched_key,
            "why": why,
            "url": catalogue[matched_key]["url"]
        })

    return results[:3]
