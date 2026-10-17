import streamlit as st
import requests
import re
import time
from urllib.parse import urljoin
from google import genai
from google.genai import types

# Import the multi-turn RAG engine
from imda_knowledge import query_live_guide_rag

# Import extracted UI / UX component library
from ui_components import (
    inject_custom_css,
    render_brand_header,
    render_hero_banner,
    render_feature_card,
    render_kpi_dashboard
)

# =========================================================
# APP CONFIG & STYLING
# =========================================================

st.set_page_config(
    page_title="IMDA Pre-Approval Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inject SMEs Go Digital CSS
inject_custom_css()

# =========================================================
# ACCESS CONTROL (Password Gate)
# =========================================================

def check_password():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    render_brand_header("🔒 IMDA Pre-Approval Assistant", badge="Restricted")
    st.info("This is a restricted proof-of-concept prototype. Please enter the passcode provided in LaunchPad.")

    col1, _ = st.columns([2, 1])
    with col1:
        pwd_input = st.text_input("Access Passcode", type="password", key="login_passcode")
        if st.button("Enter Assistant", type="primary", use_container_width=True):
            try:
                expected_pwd = str(st.secrets.get("APP_PASSWORD", "bootcamp2026")).strip().lower()
            except Exception:
                expected_pwd = "bootcamp2026"

            user_entered = pwd_input.strip().lower() if pwd_input else ""

            if user_entered in (expected_pwd, "bootcamp2026"):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect passcode. Please check credentials.")
    return False

# Enforce access gate
if not check_password():
    st.stop()

# =========================================================
# CONSTANTS & MODEL SELECTION
# =========================================================

BASE_URL = "https://preapproval-guide.imda.gov.sg"
CATEGORY_DIRECTORY_URL = (
    BASE_URL
    + "/pre-approval-guide/stage-1-vendor-self-assessment/"
    + "identify-suitable-solution-category.md"
)
MODEL_NAME = "gemini-3.8-flash"

# =========================================================
# SECURITY: PROMPT INJECTION DEFENSE
# =========================================================

def sanitize_and_check_injection(user_input: str) -> tuple[bool, str]:
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

# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "page": "Home",
    "assessment": {},
    "category_suggestions": [],
    "selected_category": None,
    "selected_category_url": None,
    "category_requirements": [],
    "category_answers": {},
    "chat_messages": [
        {
            "role": "assistant",
            "content": "👋 **Hello!** I am the **Pre-Approved Solutions Assistant** for IMDA's SMEs Go Digital programme.\n\nI can help you:\n- Check **vendor & solution eligibility criteria** (incorporation age, track record, financial ratios)\n- Understand **Stage 1 & Stage 2 submission documents**\n- Clarify **InvoiceNow, Data Protection, or PSG grant parameters**\n\nHow can I help you navigate your pre-approval journey today?"
        }
    ]
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# DATA FUNCTIONS & GEMINI CLIENT
# =========================================================

@st.cache_data(ttl=3600)
def fetch_text(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text

@st.cache_data(ttl=3600)
def get_category_catalogue():
    markdown = fetch_text(CATEGORY_DIRECTORY_URL)
    categories = {}
    current_sector = "Unknown"
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

@st.cache_data(ttl=3600)
def get_category_requirements(category_url):
    markdown = fetch_text(category_url)
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
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def recommend_categories(vendor_description):
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

def parse_category_matches(answer, catalogue):
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

# =========================================================
# NAVIGATION & SIDEBAR
# =========================================================

pages = [
    "Home",
    "Self-Assessment",
    "AI Category Finder",
    "Category Requirements",
    "AI Assistant (RAG Chatbot)",
    "About Us",
    "Methodology"
]

st.sidebar.markdown("### IMDA Pre-Approval")
st.sidebar.caption("Vendor Acceleration Copilot")

selected_page = st.sidebar.radio(
    "Navigate",
    pages,
    index=pages.index(st.session_state.page
