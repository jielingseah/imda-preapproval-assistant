import streamlit as st
import requests
import re
import time
from urllib.parse import urljoin
from google import genai
from google.genai import types

# Import the multi-turn RAG engine
from imda_knowledge import query_live_guide_rag

# Import extracted UI / UX component library including footer disclaimer
from ui_components import (
    inject_custom_css,
    render_brand_header,
    render_hero_banner,
    render_feature_card,
    render_kpi_dashboard,
    render_footer_disclaimer
)

# =========================================================
# APP CONFIG (Collapsed Sidebar for Wide Modern Layout)
# =========================================================

st.set_page_config(
    page_title="IMDA Pre-Approval Assistant | SMEs Go Digital",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# ACCESS CONTROL (Password Gate)
# =========================================================

def check_password():
    """Gives access if correct password is provided."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 IMDA Pre-Approval Assistant")
    st.caption("SMEs Go Digital — Proof-of-Concept Prototype")
    st.info("This is an authorized demonstration prototype. Please enter the passcode provided in LaunchPad.")

    col1, _ = st.columns([1, 1])
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

if not check_password():
    st.stop()

inject_custom_css()

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
    "assessment_step": 0,
    "catalog_page": 1,
    "category_suggestions": [],
    "selected_category": None,
    "selected_category_url": None,
    "category_requirements": [],
    "category_answers": {},
    "form_submitted": False,
    "sub_company": "",
    "sub_person": "",
    "sub_email": "",
    "sub_phone": "",
    "sub_inquiry": "",
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
# HOME PAGE (HERO SEARCH & VMP / PRE-APPROVAL ONBOARDING)
# =========================================================

if st.session_state.page == "Home":
    render_brand_header(
        "IMDA Pre-Approval Assistant",
        subtitle="Empowering Infocomm Media (ICM) vendors to navigate pre-approval, assess readiness, and prepare submissions for the Vendor Management Portal (VMP).",
        badge="Official Prototype"
    )

    render_hero_banner(
        "Accelerate Your SMEs Go Digital Pre-Approval",
        "The SMEs Go Digital programme supports SMEs in adopting pre-approved digital solutions with grant support. Use this copilot to assess your corporate eligibility, identify matching solution categories, and prepare your formal submission."
    )

    # 1. Main Page Hero Search Bar
    with st.container(border=True):
        st.markdown("<h4 style='font-weight:700; color:#2b0b2e; margin:0 0 6px 0;'>🔍 Search Official Pre-Approved Categories & Solutions</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:12.5px; color:#636375; margin-bottom:12px;'>Enter keywords (e.g., 'Cloud Accounting', 'Cybersecurity', 'POS System') or describe your software to find matching categories instantly.</p>", unsafe_allow_html=True)
        
        home_search_col1, home_search_col2 = st.columns([5, 1])
        with home_search_col1:
            home_query = st.text_input(
                "Search query",
                placeholder="What digital capabilities does your solution offer?",
                label_visibility="collapsed",
                key="home_hero_search_input"
            )
        with home_search_col2:
            if st.button("Find Solution →", type="primary", use_container_width=True):
                if home_query.strip():
                    st.session_state.assessment["solution_description"] = home_query.strip()
                    st.session_state.page = "AI Category Finder"
                    st.rerun()

    st.markdown("---")

    # 2. About the Pre-Approval Framework & VMP Integration
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        with st.container(border=True):
            st.markdown("#### 📘 About the IMDA Pre-Approval Guide")
            st.write(
                """
                Under the **SMEs Go Digital** initiative, pre-approved solutions are vetted for quality, 
                market readiness, and track record. Eligible SMEs adopting these solutions can receive grant support (such as PSG).
                
                This assistant automates **Stage 1: Vendor Self-Assessment**, helping digital solution vendors verify foundational 
                financial criteria, customer track record, and operational requirements prior to application.
                """
            )
            st.link_button("View Official IMDA Guide ↗", "[https://preapproval-guide.imda.gov.sg](https://preapproval-guide.imda.gov.sg)", use_container_width=True)

    with col_info2:
        with st.container(border=True):
            st.markdown("#### 🏛️ Vendor Management Portal (VMP)")
            st.write(
                """
                The **Vendor Management Portal (VMP)** is IMDA's official platform where tech vendors formally submit applications, 
                track submission milestones, manage approved solution packages, and report SME deployments.
                
                Use this copilot to detect gaps in your compliance early so that your formal submission through the VMP proceeds smoothly without delays.
                """
            )
            st.link_button("Access Vendor Management Portal (VMP) ↗", "[https://services2-stg.imda.gov.sg/VMP/Home](https://services2-stg.imda.gov.sg/VMP/Home)", use_container_width=True)

    st.markdown("---")

    # 3. Interactive Journey Cards
    st.markdown("<h3 style='font-size:20px; font-weight:800; color:#2b0b2e; margin-bottom:14px;'>Explore the Pre-Approval Journey</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        render_feature_card(
            "Stage 1: Eligibility",
            "Vendor Self-Assessment",
            "Verify incorporation age, financial ratios (positive equity, current ratio >= 1), and SME deployment benchmarks."
        )
        st.write("")
        if st.button("Start Assessment →", key="home_btn_assess", use_container_width=True):
            st.session_state.page = "Self-Assessment"
            st.rerun()

    with col2:
        render_feature_card(
            "Stage 2: Discovery",
            "AI Category Finder",
            "Semantic category matching powered by Gemini or browse the interactive directory with numbered pagination."
        )
        st.write("")
        if st.button("Browse Categories →", key="home_btn_cat", use_container_width=True):
            st.session_state.page = "AI Category Finder"
            st.rerun()

    with col3:
        render_feature_card(
            "Stage 3: Guidance",
            "AI Assistant (RAG Chatbot)",
            "Engage our conversational copilot grounded in real-time IMDA pre-approval documentation."
        )
        st.write("")
        if st.button("Launch Copilot →", key="home_btn_chat", type="primary", use_container_width=True):
            st.session_state.page = "AI Assistant"
            st.rerun()

    render_footer_disclaimer()

# =========================================================
# SELF-ASSESSMENT (ROBUST MOBILE-FRIENDLY WIZARD)
# =========================================================

elif st.session_state.page == "Self-Assessment":
    render_brand_header("Vendor Self-Assessment", subtitle="Prerequisite validation against mandatory onboarding standards.")
    
    steps = ["1. Vendor Eligibility", "2. Solution Track Record", "3. Solution Eligibility"]
    progress_vals = [0.33, 0.66, 1.0]
    st.progress(progress_vals[st.session_state.assessment_step], text=f"Validation in Progress — Step {st.session_state.assessment_step + 1} of 3")

    selected_tab = st.radio("Assessment Section", steps, index=st.session_state.assessment_step, horizontal=True, key="assessment_wizard_radio")
    st.session_state.assessment_step = steps.index(selected_tab)

    st.markdown("---")

    if st.session_state.assessment_step == 0:
        st.markdown("### 🏢 Vendor Eligibility Standards")
        st.caption("Confirm foundational corporate and financial prerequisites.")

        vendor_questions = [
            ("incorporated", "Is your company incorporated in Singapore?", ["Yes", "No"]),
            ("operation", "Has your company been in operation for at least 18 months?", ["Yes", "No"]),
            ("financial", "Is your company financially stable (positive net equity, current ratio >= 1)?", ["Yes", "No", "Not sure"]),
            ("track_record", "Does your company have satisfactory track record with government agencies?", ["Yes", "No", "Not currently, but development is underway"]),
            ("resources", "Does your company have sufficient quality resources?", ["Yes", "No", "Not sure"]),
            ("cooling", "Is your company currently serving a one-year cooling period from IMDA?", ["Yes", "No"]),
            ("invoice_now", "Has your company signed up for an InvoiceNow account?", ["Yes", "No", "Not currently, but development is underway"])
        ]

        for key, question, options in vendor_questions:
            with st.container(border=True):
                current_val = st.session_state.assessment.get(key, options[0])
                idx = options.index(current_val) if current_val in options else 0
                st.session_state.assessment[key] = st.radio(question, options, index=idx, key=f"vendor_{key}")

        st.markdown("")
        col_b1, col_b2 = st.columns([1, 1])
        with col_b2:
            if st.button("Save & Continue to Track Record →", type="primary", use_container_width=True):
                st.session_state.assessment_step = 1
                st.rerun()

    elif st.session_state.assessment_step == 1:
        st.markdown("### 📊 Solution Track Record & Deployment")
        st.caption("Specify market reach and SME customer base metrics.")

        with st.container(border=True):
            ind_options = ["Many industries", "One or few industries", "Not sure"]
            current_ind = st.session_state.assessment.get("industries", ind_options[0])
            ind_idx = ind_options.index(current_ind) if current_ind in ind_options else 0
            industries = st.radio(
                "Select the statement that best describes the industries your solution caters to.",
                ind_options,
                index=ind_idx,
                key="industries"
            )
            st.session_state.assessment["industries"] = industries

        if industries == "One or few industries":
            with st.container(border=True):
                track_opts = ["Yes", "No", "Not sure"]
                current_track = st.session_state.assessment.get("customer_track", track_opts[0])
                track_idx = track_opts.index(current_track) if current_track in track_opts else 0
                st.session_state.assessment["customer_track"] = st.radio(
                    "Has your solution been deployed with at least 5 Singapore-registered SMEs for at least 6 months?",
                    track_opts,
                    index=track_idx,
                    key="customer_track"
                )

        st.markdown("")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("← Previous Step", use_container_width=True):
                st.session_state.assessment_step = 0
                st.rerun()
        with col_b2:
            if st.button("Save & Continue to Solution Eligibility →", type="primary", use_container_width=True):
                st.session_state.assessment_step = 2
                st.rerun()

    elif st.session_state.assessment_step == 2:
        st.markdown("### ⚙️ Solution Specifications & Value")
        st.caption("Verify pricing, suitability, productivity impact, and compliance.")

        solution_questions = [
            ("pricing", "Is your solution priced reasonably for SMEs?", ["Yes", "No", "Not sure"]),
            ("suitability", "Is your solution designed to suit the needs and demands of SMEs?", ["Yes", "No", "Not sure"]),
            ("productivity", "Does your solution help SMEs improve productivity?", ["Yes", "No", "Not sure"]),
            ("website", "Do you have a website that showcases the solution?", ["Yes", "No", "Not currently, but development is underway"]),
            ("dapdp", "Have you validated compliance with Data Analytics and Personal Data Protection requirements?", ["Yes", "No", "Not currently, but development is underway"])
        ]

        for key, question, options in solution_questions:
            with st.container(border=True):
                current_val = st.session_state.assessment.get(key, options[0])
                idx = options.index(current_val) if current_val in options else 0
                st.session_state.assessment[key] = st.radio(question, options, index=idx, key=f"solution_{key}")

        st.markdown("---")
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            if st.button("← Previous Step", use_container_width=True):
                st.session_state.assessment_step = 1
                st.rerun()
        with col_b2:
            if st.button("Complete Assessment & Find Solution Category →", type="primary", use_container_width=True):
                st.session_state.page = "AI Category Finder"
                st.rerun()

    render_footer_disclaimer()

# =========================================================
# AI CATEGORY FINDER & PAGINATED MANUAL BROWSER
# =========================================================

elif st.session_state.page == "AI Category Finder":
    st.markdown('<script>window.scrollTo(0, 0);</script>', unsafe_allow_html=True)
    render_brand_header("Solution Category Discovery", subtitle="Identify your pre-approved solution category using AI semantic matching or manual directory browsing.")

    tab_ai, tab_manual = st.tabs(["🤖 AI Semantic Matcher", "🔍 Manual Directory Browser"])

    with tab_ai:
        st.markdown("<p style='font-size: 13.5px; color: #636375; margin-bottom: 12px;'>Describe your solution features to let Gemini match you with the best official IMDA categories.</p>", unsafe_allow_html=True)
        
        with st.container(border=True):
            description = st.text_area(
                "Describe your solution capabilities",
                height=110,
                value=st.session_state.assessment.get("solution_description", ""),
                placeholder="Example: We provide a cloud inventory management system with automated POS reconciliation and e-invoicing for retail SMEs."
            )
            st.session_state.assessment["solution_description"] = description

            if st.button("Find Matching Categories via AI →", type="primary", use_container_width=True):
                is_safe, sanitized_text = sanitize_and_check_injection(description)
                if not is_safe:
                    st.error(sanitized_text)
                else:
                    with st.spinner("Analyzing against official IMDA categories..."):
                        result = recommend_categories(sanitized_text)

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        matches = parse_category_matches(result["answer"], result["catalogue"])
                        st.session_state.category_suggestions = matches

        if st.session_state.category_suggestions:
            st.markdown("---")
            st.markdown("<h5 style='font-size: 16px; font-weight: 700; color: #581845;'>💡 AI Recommended Matches</h5>", unsafe_allow_html=True)
            for index, suggestion in enumerate(st.session_state.category_suggestions):
                category_key = suggestion["category_key"]
                catalogue = get_category_catalogue()
                category = catalogue.get(category_key, {"url": "#", "description": ""})

                with st.container(border=True):
                    st.markdown(f"<h6 style='font-size: 15px; font-weight: 700; color: #2b0b2e;'>{index + 1}. {category_key}</h6>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-size: 12.5px; color: #555566;'>{suggestion['why']}</p>", unsafe_allow_html=True)
                    if st.button("Confirm & Select AI Category", key=f"select_ai_cat_{index}", use_container_width=True):
                        st.session_state.selected_category = category_key
                        st.session_state.selected_category_url = category["url"]
                        st.session_state.page = "Category Requirements"
                        st.rerun()

    with tab_manual:
        st.markdown("<p style='font-size: 13.5px; color: #636375; margin-bottom: 12px;'>Browse all valid IMDA solution categories by sector or search keywords with numbered pagination.</p>", unsafe_allow_html=True)

        try:
            catalogue = get_category_catalogue()
            if catalogue:
                sectors = sorted(list(set([val["sector"] for val in catalogue.values()])))
                
                selected_sector = st.radio(
                    "Filter by Sector",
                    ["All Sectors"] + sectors,
                    horizontal=True,
                    key="interactive_sector_filter"
                )

                search_query = st.text_input("Search categories by keyword", placeholder="e.g. Cybersecurity, Invoicing, POS...", key="cat_search_query")

                filtered_items = []
                for k, v in catalogue.items():
                    if selected_sector != "All Sectors" and v["sector"] != selected_sector:
                        continue
                    if search_query.strip() and search_query.lower() not in k.lower() and search_query.lower() not in v["description"].lower():
                        continue
                    filtered_items.append((k, v))

                total_items = len(filtered_items)
                items_per_page = 6

                if total_items > 0:
                    total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

                    if "catalog_page" not in st.session_state:
                        st.session_state.catalog_page = 1
                    if st.session_state.catalog_page > total_pages:
                        st.session_state.catalog_page = total_pages

                    st.markdown(f"<p style='font-size: 12px; color: #777788; margin-top: 8px;'>Showing {total_items} matching categories (Page {st.session_state.catalog_page} of {total_pages})</p>", unsafe_allow_html=True)

                    start_idx = (st.session_state.catalog_page - 1) * items_per_page
                    end_idx = min(start_idx + items_per_page, total_items)
                    page_items = filtered_items[start_idx:end_idx]

                    for i in range(0, len(page_items), 2):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if i < len(page_items):
                                k1, v1 = page_items[i]
                                with st.container(border=True):
                                    st.markdown(f"<span style='background:#f7eaf3; color:#7a1d5a; padding:1px 6px; border-radius:4px; font-size:10px; font-weight:700;'>{v1['sector']}</span>", unsafe_allow_html=True)
                                    st.markdown(f"<h6 style='font-size: 14.5px; font-weight: 700; color: #2b0b2e; margin-top: 6px;'>{v1['category']}</h6>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='font-size: 12px; color: #636375; line-height: 1.4;'>{v1['description'] if v1['description'] else 'Official IMDA pre-approved solution category.'}</p>", unsafe_allow_html=True)
                                    if st.button("Select Category →", key=f"manual_card_{start_idx + i}", use_container_width=True):
                                        st.session_state.selected_category = k1
                                        st.session_state.selected_category_url = v1["url"]
                                        st.session_state.page = "Category Requirements"
                                        st.rerun()

                        with col2:
                            if i + 1 < len(page_items):
                                k2, v2 = page_items[i + 1]
                                with st.container(border=True):
                                    st.markdown(f"<span style='background:#f7eaf3; color:#7a1d5a; padding:1px 6px; border-radius:4px; font-size:10px; font-weight:700;'>{v2['sector']}</span>", unsafe_allow_html=True)
                                    st.markdown(f"<h6 style='font-size: 14.5px; font-weight: 700; color: #2b0b2e; margin-top: 6px;'>{v2['category']}</h6>", unsafe_allow_html=True)
                                    st.markdown(f"<p style='font-size: 12px; color: #636375; line-height: 1.4;'>{v2['description'] if v2['description'] else 'Official IMDA pre-approved solution category.'}</p>", unsafe_allow_html=True)
                                    if st.button("Select Category →", key=f"manual_card_{start_idx + i + 1}", use_container_width=True):
                                        st.session_state.selected_category = k2
                                        st.session_state.selected_category_url = v2["url"]
                                        st.session_state.page = "Category Requirements"
                                        st.rerun()

                    st.markdown("---")
                    page_cols = st.columns(min(total_pages, 10))
                    for p_num in range(1, total_pages + 1):
                        col_idx = (p_num - 1) % 10
                        with page_cols[col_idx]:
                            btn_type = "primary" if p_num == st.session_state.catalog_page else "secondary"
                            if st.button(str(p_num), key=f"page_num_{p_num}", type=btn_type, use_container_width=True):
                                st.session_state.catalog_page = p_num
                                st.rerun()
                else:
                    st.info("No categories match your current sector filter or search keyword.")
            else:
                st.warning("Catalogue could not be loaded at this moment.")
        except Exception as e:
            st.error(f"Error loading interactive catalogue: {e}")

    render_footer_disclaimer()

# =========================================================
# CATEGORY REQUIREMENTS & GAP AUDIT / SUBMISSION
# =========================================================

elif st.session_state.page == "Category Requirements":
    render_brand_header(
        "Category Requirements & Pre-Submission Review",
        subtitle="Specific functional checklist, prerequisite gap analysis, and enquiry submission."
    )
    selected = st.session_state.selected_category

    if not selected:
        with st.container(border=True):
            st.info("Please select a solution category first.")
            if st.button("← Back to Category Finder", type="primary"):
                st.session_state.page = "AI Category Finder"
                st.rerun()
    else:
        catalogue = get_category_catalogue()
        category = catalogue.get(selected, {"description": "Official IMDA category checklist.", "url": "#"})
        
        with st.container(border=True):
            st.success(f"Selected Category: **{selected}**")
            st.write(category["description"])
            st.link_button("Open official IMDA requirements page", category["url"])

        st.markdown("---")
        with st.spinner("Loading official checklist..."):
            requirements = get_category_requirements(category["url"])

        mandatory = [q for q in requirements if q["mandatory"]]
        preferred = [q for q in requirements if not q["mandatory"]]

        if not mandatory:
            st.warning("Requirements could not be extracted automatically. Please verify via the link above.")
        else:
            st.subheader("1. Mandatory Functional Checklist")
            st.caption("Indicate your solution's current compliance status for each item below.")

            for question in mandatory:
                key = f"category_q_{question['number']}"
                existing_ans = st.session_state.category_answers.get(question["number"], "Yes")
                ans_opts = ["Yes", "No", "Not sure"]
                ans_idx = ans_opts.index(existing_ans) if existing_ans in ans_opts else 0

                with st.container(border=True):
                    st.session_state.category_answers[question["number"]] = st.radio(
                        f"Q{question['number']} — {question['question']}",
                        ans_opts,
                        index=ans_idx,
                        key=key
                    )

            if preferred:
                with st.expander(f"View {len(preferred)} Preferred Requirements"):
                    for question in preferred:
                        with st.container(border=True):
                            st.write(f"**Q{question['number']}** — {question['question']}")

            st.markdown("
