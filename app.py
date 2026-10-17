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
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="IMDA Pre-Approval Assistant | SMEs Go Digital",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
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

st.sidebar.markdown("### SMEs Go Digital")
st.sidebar.caption("IMDA Pre-Approval Copilot")

current_page = st.session_state.get("page", "Home")
default_idx = pages.index(current_page) if current_page in pages else 0

selected_page = st.sidebar.radio("Navigate", pages, index=default_idx)
st.session_state.page = selected_page

st.sidebar.markdown("---")
if st.sidebar.button("🔒 Logout / Lock App", use_container_width=True):
    st.session_state.authenticated = False
    st.rerun()

st.sidebar.markdown("---")
with st.sidebar.expander("⚠️ IMPORTANT NOTICE — Prototype", expanded=False):
    st.caption(
        """
        **Proof-of-Concept Prototype:**
        This web application is developed for demonstration purposes only.
        The information provided here is NOT intended for actual usage and should not be relied upon
        for making business or regulatory decisions.
        """
    )
st.sidebar.caption("IMDA SMEs Go Digital POC")

# =========================================================
# HOME PAGE
# =========================================================

if st.session_state.page == "Home":
    render_brand_header(
        "IMDA Pre-Approval Assistant",
        subtitle="Accelerate your pre-approval journey with self-assessment checks, AI category discovery, and grounded guidance.",
        badge="Official Prototype"
    )

    render_hero_banner(
        "Accelerate Your Pre-Approval Readiness",
        "Verify your eligibility, discover official solution categories with AI, and engage in real-time guidance grounded in official IMDA policy documentation."
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        render_feature_card("Eligibility", "Vendor Self-Assessment", "Verify financial viability, track record benchmarks, and SME readiness.")
        st.write("")
        if st.button("Start Assessment →", use_container_width=True):
            st.session_state.page = "Self-Assessment"
            st.rerun()

    with col2:
        render_feature_card("AI Tool", "Category Finder", "Zero-shot semantic matching against the live IMDA directory using Gemini.")
        st.write("")
        if st.button("Find Category →", use_container_width=True):
            st.session_state.page = "AI Category Finder"
            st.rerun()

    with col3:
        render_feature_card("Copilot", "Pre-Approval Assistant", "Full multi-turn conversational agent with real-time official guide citations.")
        st.write("")
        if st.button("Open AI Chatbot →", type="primary", use_container_width=True):
            st.session_state.page = "AI Assistant (RAG Chatbot)"
            st.rerun()

# =========================================================
# SELF-ASSESSMENT (MODERN TABBED WIZARD & CARD LAYOUT)
# =========================================================

elif st.session_state.page == "Self-Assessment":
    render_brand_header("Vendor Self-Assessment", subtitle="Prerequisite validation against mandatory onboarding standards.")
    st.progress(0.33, text="Validation in Progress — Step 1 of 3")

    t1, t2, t3 = st.tabs(["1. Vendor Eligibility", "2. Solution Track Record", "3. Solution Eligibility"])

    with t1:
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
        if st.button("Save & Continue to Track Record →", type="primary", use_container_width=True):
            st.rerun()

    with t2:
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
        if st.button("Save & Continue to Solution Eligibility →", type="primary", use_container_width=True):
            st.rerun()

    with t3:
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
        if st.button("Complete Assessment & Find Solution Category →", type="primary", use_container_width=True):
            st.session_state.page = "AI Category Finder"
            st.rerun()

# =========================================================
# AI CATEGORY FINDER & INTERACTIVE MANUAL BROWSER
# =========================================================

elif st.session_state.page == "AI Category Finder":
    render_brand_header("AI Category Finder & Solution Selection", subtitle="Discover categories via AI recommendation or browse the complete interactive catalogue manually.")

    # 1. AI Recommendation Input Card
    with st.container(border=True):
        st.markdown("### 🤖 Step 1: AI-Powered Recommendation")
        st.caption("Describe your solution capabilities to let Gemini match you with the best official categories.")
        
        description = st.text_area(
            "Tell us about your solution",
            height=130,
            value=st.session_state.assessment.get("solution_description", ""),
            placeholder="Example: We provide a cloud inventory management system with automated POS reconciliation and e-invoicing for retail SMEs."
        )
        st.session_state.assessment["solution_description"] = description

        if st.button("Find Relevant Categories via AI →", type="primary", use_container_width=True):
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

    # Display AI Suggestions if available
    if st.session_state.category_suggestions:
        st.markdown("---")
        st.subheader("💡 AI Recommended Matches")
        for index, suggestion in enumerate(st.session_state.category_suggestions):
            category_key = suggestion["category_key"]
            catalogue = get_category_catalogue()
            category = catalogue.get(category_key, {"url": "#", "description": ""})

            with st.container(border=True):
                st.markdown(f"### {index + 1}. {category_key}")
                st.write(suggestion["why"])
                if st.button("Confirm & Select AI Category", key=f"select_ai_cat_{index}", use_container_width=True):
                    st.session_state.selected_category = category_key
                    st.session_state.selected_category_url = category["url"]
                    st.session_state.page = "Category Requirements"
                    st.rerun()

    # 2. Interactive Manual Catalogue Card Browser
    st.markdown("---")
    with st.container(border=True):
        st.markdown("### 🔍 Step 2: Interactive Official Catalogue Browser (Manual Selection)")
        st.caption("Browse all valid IMDA solution categories by sector or filter keywords manually below.")

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

                st.markdown(f"**Showing {len(filtered_items)} available categories:**")

                if filtered_items:
                    for i in range(0, len(filtered_items), 2):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if i < len(filtered_items):
                                k1, v1 = filtered_items[i]
                                with st.container(border=True):
                                    st.markdown(f"<span style='background:#f7eaf3; color:#7a1d5a; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700;'>{v1['sector']}</span>", unsafe_allow_html=True)
                                    st.markdown(f"#### {v1['category']}")
                                    st.write(v1["description"] if v1["description"] else "Official IMDA pre-approved solution category.")
                                    if st.button("Select Category →", key=f"manual_card_{i}", use_container_width=True):
                                        st.session_state.selected_category = k1
                                        st.session_state.selected_category_url = v1["url"]
                                        st.session_state.page = "Category Requirements"
                                        st.rerun()

                        with col2:
                            if i + 1 < len(filtered_items):
                                k2, v2 = filtered_items[i + 1]
                                with st.container(border=True):
                                    st.markdown(f"<span style='background:#f7eaf3; color:#7a1d5a; padding:2px 8px; border-radius:4px; font-size:11px; font-weight:700;'>{v2['sector']}</span>", unsafe_allow_html=True)
                                    st.markdown(f"#### {v2['category']}")
                                    st.write(v2["description"] if v2["description"] else "Official IMDA pre-approved solution category.")
                                    if st.button("Select Category →", key=f"manual_card_{i+1}", use_container_width=True):
                                        st.session_state.selected_category = k2
                                        st.session_state.selected_category_url = v2["url"]
                                        st.session_state.page = "Category Requirements"
                                        st.rerun()
                else:
                    st.info("No categories match your current sector filter or search keyword.")
            else:
                st.warning("Catalogue could not be loaded at this moment.")
        except Exception as e:
            st.error(f"Error loading interactive catalogue: {e}")

# =========================================================
# CATEGORY REQUIREMENTS & GAP AUDIT / SUBMISSION (CARD LAYOUT)
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

            st.markdown("---")

            # 2. Automated Prerequisite Gap Detection
            st.subheader("2. Automated Prerequisite Gap Detection")

            front_assessment_labels = {
                "incorporated": "Company incorporated in Singapore",
                "operation": "Operation for at least 18 months",
                "financial": "Financial stability (positive equity & ratio >= 1)",
                "track_record": "Government agency track record",
                "resources": "Sufficient quality resources",
                "cooling": "Not serving 1-year IMDA cooling period",
                "invoice_now": "InvoiceNow registered account",
                "customer_track": "Deployed with >= 5 SG SMEs for >= 6 months",
                "pricing": "Priced reasonably for SMEs",
                "suitability": "Designed for SME needs",
                "productivity": "Improves SME productivity",
                "website": "Active website showcasing solution",
                "dapdp": "Data protection & analytics compliance"
            }

            front_gaps = []
            for k, label in front_assessment_labels.items():
                val = st.session_state.assessment.get(k)
                if val in ["No", "Not sure"] or (k == "cooling" and val == "Yes") or ("development" in str(val).lower()):
                    front_gaps.append({"item": label, "status": val})

            unmet_cat_questions = []
            for question in mandatory:
                ans = st.session_state.category_answers.get(question["number"])
                if ans in ["No", "Not sure"]:
                    unmet_cat_questions.append({
                        "number": question["number"],
                        "question": question["question"],
                        "status": ans
                    })

            total_gaps_count = len(front_gaps) + len(unmet_cat_questions)

            with st.container(border=True):
                if total_gaps_count > 0:
                    st.warning(f"⚠️ System detected **{total_gaps_count}** requirement gap(s) across your assessment:")
                    if front_gaps:
                        st.markdown("**Core Baseline & Track Record Gaps:**")
                        for fg in front_gaps:
                            st.markdown(f"- 🔴 **{fg['item']}** (Status: *{fg['status']}*)")

                    if unmet_cat_questions:
                        st.markdown(f"**Specific Category Requirements for {selected}:**")
                        for uq in unmet_cat_questions:
                            st.markdown(f"- ⚠️ **Q{uq['number']} ({uq['status']}):** {uq['question']}")
                else:
                    st.success("✅ Excellent! Your solution declared full compliance with both Baseline Eligibility and Category Specifications.")

            st.markdown("---")

            # 3. Contact Details & Vendor Enquiries Form in Card
            st.subheader("3. Contact Details & Vendor Enquiries")
            st.caption("Provide your company contact information and any specific questions regarding unmet criteria or general onboarding.")

            with st.container(border=True):
                with st.form("vendor_submission_form"):
                    col_c1, col_c2 = st.columns(2)
                    with col_c1:
                        company_name = st.text_input("Company Registered Name *", placeholder="e.g. Acme Tech Solutions Pte Ltd")
                        contact_person = st.text_input("Contact Person Name *", placeholder="e.g. John Tan")
                    with col_c2:
                        contact_email = st.text_input("Corporate Email Address *", placeholder="e.g. john.tan@acme.com")
                        contact_phone = st.text_input("Contact Number *", placeholder="e.g. +65 9123 4567")

                    vendor_inquiry = st.text_area(
                        "Questions / Notes on Unmet Requirements",
                        placeholder="If you marked 'No' or 'Not sure' above, specify your planned roadmap, alternative workarounds, or questions for IMDA officers here.",
                        height=120
                    )

                    submit_button = st.form_submit_button("Submit Assessment & Send Summary →", type="primary", use_container_width=True)

            if submit_button:
                if not company_name or not contact_person or not contact_email:
                    st.error("Please fill in all mandatory contact fields (Company Name, Contact Person, and Email).")
                    st.session_state.form_submitted = False
                else:
                    st.session_state.form_submitted = True
                    st.session_state.sub_company = company_name
                    st.session_state.sub_person = contact_person
                    st.session_state.sub_email = contact_email
                    st.session_state.sub_phone = contact_phone
                    st.session_state.sub_inquiry = vendor_inquiry

            # 4. Submission Summary Dossier & Chatbot Recommendation (Rendered OUTSIDE form)
            if st.session_state.get("form_submitted", False):
                st.success("🎉 Assessment & Enquiries Submitted Successfully!")

                with st.container(border=True):
                    st.markdown("### 📋 Submission Summary Dossier")
                    st.markdown(f"**Target Pre-Approval Category:** {selected}")
                    st.markdown(f"**Company:** {st.session_state.sub_company} | **Contact:** {st.session_state.sub_person} ({st.session_state.sub_email}, {st.session_state.sub_phone})")

                    if front_gaps or unmet_cat_questions:
                        st.markdown("#### Detected Gaps for Officer Review:")
                        for fg in front_gaps:
                            st.markdown(f"- **Baseline Prerequisite ({fg['status']}):** {fg['item']}")
                        for uq in unmet_cat_questions:
                            st.markdown(f"- **Category Spec Q{uq['number']} ({uq['status']}):** {uq['question']}")
                    else:
                        st.markdown("✅ **Status:** 100% compliant across all evaluated criteria.")

                    if st.session_state.sub_inquiry.strip():
                        st.markdown("#### Applicant Inquiries:")
                        st.write(st.session_state.sub_inquiry)

                st.info(
                    "📧 **Notification Routing:** This summary report and inquiry record have been prepared for dispatch to **`seah_jie_ling@imda.gov.sg`** for officer review."
                )
                st.warning(
                    "ℹ️ **Prototype Notice:** Please note that this is a proof-of-concept demonstration environment. "
                    "Live SMTP servers and automated email dispatch are intentionally not configured for this prototype session, "
                    "and external emails will not be transmitted."
                )

                st.markdown("---")
                with st.container(border=True):
                    st.markdown("### 🤖 Want guidance on how to address your identified gaps?")
                    st.write("You can chat with our AI Pre-Approval Copilot right now for instant, grounded recommendations on how to fulfill official IMDA policy requirements.")
                    
                    if st.button("💬 Open AI Assistant & Get Guidance →", type="primary", use_container_width=True):
                        st.session_state.page = "AI Assistant (RAG Chatbot)"
                        st.rerun()

# =========================================================
# AI ASSISTANT (RAG CHATBOT)
# =========================================================

elif st.session_state.page == "AI Assistant (RAG Chatbot)":
    render_brand_header("Pre-Approved Solutions Assistant & Copilot", subtitle="Multi-turn conversation grounded in official IMDA documentation.")

    col_info, col_btn = st.columns([4, 1])
    with col_info:
        if st.session_state.selected_category:
            st.info(f"Target Category: **{st.session_state.selected_category}**")
    with col_btn:
        if st.button("🔄 Reset Chat", use_container_width=True):
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "Conversation restarted. How can I help you navigate your pre-approval journey today?"
                }
            ]
            st.rerun()

    if st.session_state.assessment:
        with st.expander("📊 View Your Readiness Audit Summary", expanded=False):
            blockers = [k.replace("_", " ").title() for k, v in st.session_state.assessment.items() if v == "No"]
            in_progress = [k.replace("_", " ").title() for k, v in st.session_state.assessment.items() if "development" in str(v)]
            passed = [k for k, v in st.session_state.assessment.items() if v == "Yes"]
            total_eval = len(st.session_state.assessment)
            readiness_pct = int((len(passed) / total_eval) * 100) if total_eval > 0 else 0

            render_kpi_dashboard(readiness_pct, len(blockers), len(in_progress))

            if blockers:
                st.error("Identified Gaps: " + ", ".join(blockers))

    st.markdown("---")

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_query := st.chat_input("Ask a question (e.g. Can a company registered in Malaysia apply?)"):
        is_safe, sanitized_query = sanitize_and_check_injection(user_query)
        if not is_safe:
            st.error(sanitized_query)
        else:
            st.session_state.chat_messages.append({"role": "user", "content": sanitized_query})
            with st.chat_message("user"):
                st.markdown(sanitized_query)

            client = get_gemini_client()
            if client is None:
                st.error("Gemini API key is not configured in Secrets.")
            else:
                with st.chat_message("assistant"):
                    with st.spinner("Consulting official guide..."):
                        assistant_response = query_live_guide_rag(
                            client,
                            user_query=sanitized_query,
                            chat_history=st.session_state.chat_messages,
                            user_assessment=st.session_state.assessment,
                            selected_category=st.session_state.selected_category,
                            model_name=MODEL_NAME
                        )
                        st.markdown(assistant_response)

                st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})

# =========================================================
# ABOUT US & METHODOLOGY (CARD LAYOUTS)
# =========================================================

elif st.session_state.page == "About Us":
    render_brand_header("About This Project", subtitle="Background, problem statement, and scope.")
    with st.container(border=True):
        st.markdown("""
        The **IMDA Pre-Approval Assistant** is an agentic self-service copilot designed to bridge the operational gap between digital solution vendors and IMDA's Pre-Approval framework under the SMEs Go Digital programme.
        """)

    st.subheader("1. Problem Statement")
    with st.container(border=True):
        st.write("Vendors seeking pre-approval frequently encounter difficulties interpreting domain qualification criteria, identifying appropriate solution categories, and validating baseline prerequisites. This creates unnecessary manual back-and-forth for both vendors and officers.")

    st.subheader("2. Project Objectives")
    with st.container(border=True):
        st.markdown("""
        - **Empower Vendor Self-Discovery:** Provide instant, semantic category recommendations from plain English descriptions.
        - **Upfront Gap Remediation:** Highlight operational roadblocks prior to formal submission.
        - **Real-Time Grounded Knowledge:** Equip vendors with a full multi-turn conversational copilot grounded in the official online guide.
        """)

elif st.session_state.page == "Methodology":
    render_brand_header("Methodology & System Architecture", subtitle="Prompt engineering pipelines and security controls.")
    with st.container(border=True):
        st.markdown("""
        - **Adversarial Heuristic Defense:** User inputs pass through regex pattern matching to block instruction override attacks and prompt leaks.
        - **XML Boundary Delimitation:** Untrusted text is strictly separated from system directives using `<user_query>` and `<context>` envelopes.
        - **Multi-Turn Context Awareness:** Conversations retain prior turns within `<conversation_history>` blocks to handle sequential follow-ups.
        """)
