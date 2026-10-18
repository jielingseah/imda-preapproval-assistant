import streamlit as st
from google import genai

# Centralized constants and RAG engine
from imda_knowledge import (
    MODEL_NAME,
    STAGE_2_GUIDE_URL,
    VMP_PORTAL_URL,
    query_live_guide_rag
)

# UI/UX Design System
from ui_components import (
    inject_custom_css,
    render_brand_header,
    render_hero_banner,
    render_feature_card,
    render_footer_disclaimer
)

# Assessment Domain Engine & Security Service
from assessment_service import sanitize_and_check_injection
from assessment_module import render_pre_approval_assessment

# =========================================================
# APP CONFIG (Wide Modern Portal Layout)
# =========================================================

st.set_page_config(
    page_title="IMDA Pre-Approval Assistant | SMEs Go Digital",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# ACCESS CONTROL (Strict Secrets Authentication)
# =========================================================

def check_password():
    """Gives access only if correct password configured in Streamlit Secrets is provided."""
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
            configured_pwd = str(st.secrets.get("APP_PASSWORD", "")).strip().lower()
            user_entered = pwd_input.strip().lower() if pwd_input else ""

            if not configured_pwd:
                st.error("Authentication configuration error: 'APP_PASSWORD' is not set in Streamlit Secrets.")
            elif user_entered == configured_pwd:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Incorrect passcode. Please check credentials.")
    return False

if not check_password():
    st.stop()

inject_custom_css()

# Anchor point for instant return to top
st.markdown('<div id="page-top"></div>', unsafe_allow_html=True)

# =========================================================
# SESSION STATE DEFAULTS
# =========================================================

defaults = {
    "page": "Home",
    "assessment": {},
    "assessment_step": 0,
    "catalog_page": 1,
    "category_suggestions": [],
    "auto_trigger_search": False,
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
    "show_chat_dialog": False,
    "prereq_tab_idx": 0,
    "chat_messages": [
        {
            "role": "assistant",
            "content": "👋 **Hello!** I am the **Pre-Approved Solutions Copilot** for IMDA's SMEs Go Digital programme.\n\nAsk me anything about:\n- **Eligibility criteria** (financial stability, incorporation age)\n- **Category requirements** and functional checklists\n- **InvoiceNow, Data Protection**, or PSG parameters"
        }
    ]
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

# =========================================================
# FLOATING PERSISTENT RAG CHATBOT DIALOG
# =========================================================

@st.dialog("💬 IMDA Pre-Approval AI Copilot", width="large")
def render_floating_chat_modal():
    st.caption("Ask questions grounded in live IMDA pre-approval policy documentation.")
    
    col_t1, col_t2 = st.columns([3, 1])
    with col_t1:
        if st.session_state.selected_category:
            st.info(f"Target Category: **{st.session_state.selected_category}**")
    with col_t2:
        if st.button("🔄 Reset", key="modal_reset_chat", use_container_width=True):
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "Conversation restarted. How can I help you navigate your pre-approval journey today?"
                }
            ]
            st.rerun()

    chat_box = st.container(height=360)
    with chat_box:
        for msg in st.session_state.chat_messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])

    if user_prompt := st.chat_input("Ask a question about pre-approval or addressing your gaps..."):
        is_safe, sanitized_query = sanitize_and_check_injection(user_prompt)
        if not is_safe:
            st.error(sanitized_query)
        else:
            st.session_state.chat_messages.append({"role": "user", "content": sanitized_query})
            client = get_gemini_client()
            if client:
                with st.spinner("Consulting official guide..."):
                    assistant_response = query_live_guide_rag(
                        client,
                        user_query=sanitized_query,
                        chat_history=st.session_state.chat_messages,
                        user_assessment=st.session_state.assessment,
                        selected_category=st.session_state.selected_category,
                        model_name=MODEL_NAME
                    )
                st.session_state.chat_messages.append({"role": "assistant", "content": assistant_response})
            st.rerun()

if st.session_state.show_chat_dialog:
    render_floating_chat_modal()
    st.session_state.show_chat_dialog = False

# =========================================================
# PAGE 1: HOME PAGE (STRUCTURED STAGE 1 & STAGE 2)
# =========================================================

if st.session_state.page == "Home":
    render_brand_header(
        "IMDA Pre-Approval Assistant",
        subtitle="Empowering Infocomm Media (ICM) vendors to navigate pre-approval, assess readiness, and prepare submissions for the Vendor Management Portal (VMP).",
        badge="Official Prototype"
    )

    render_hero_banner(
        "Accelerate Your SMEs Go Digital Pre-Approval",
        "The SMEs Go Digital programme supports SMEs in adopting pre-approved digital solutions with grant support. Use this copilot to check your category feasibility, assess corporate eligibility, and prepare your formal submission."
    )

    st.markdown("<h3 class='portal-section-heading'>The Pre-Approval Journey (Stage 1: Vendor Self-Assessment)</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            """
            <div class="portal-spacer-sm">
                <span class="step-badge">
                    <span>🔍</span> STEP 1: DISCOVERY & FEASIBILITY
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<h4 class='portal-card-title'>🔍 Solution Category Pre-Check</h4>", unsafe_allow_html=True)
        st.markdown(
            """
            <p class="portal-section-subtext">
                Check if your solution fits an official IMDA category before starting self-assessment. 
                If your product does not fall under an existing pre-approved category, it is not eligible under this programme.
            </p>
            """,
            unsafe_allow_html=True
        )
        
        home_search_col1, home_search_col2 = st.columns([5, 1.4])
        with home_search_col1:
            home_query = st.text_input(
                "Search query",
                placeholder='e.g., "my solution helps manage pre-school operations" or "my solution manages SEO/SEM digital marketing campaigns"',
                label_visibility="collapsed",
                key="home_hero_search_input"
            )
        with home_search_col2:
            if st.button("Check Category →", type="primary", use_container_width=True):
                if home_query.strip():
                    st.session_state.assessment["solution_description"] = home_query.strip()
                    st.session_state.auto_trigger_search = True
                    st.session_state.page = "Pre-Approval Assessment"
                    st.session_state.assessment_step = 0
                    st.rerun()

        st.markdown("<p class='portal-hint-text'>💡 Or click a sample prompt to try:</p>", unsafe_allow_html=True)
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            if st.button("🏫 Pre-School Operations", key="sample_prompt_1", use_container_width=True):
                st.session_state.assessment["solution_description"] = "My solution helps manage pre-school operations, student attendance, parent communications, and fee collection."
                st.session_state.auto_trigger_search = True
                st.session_state.page = "Pre-Approval Assessment"
                st.session_state.assessment_step = 0
                st.rerun()
        with s_col2:
            if st.button("📈 SEO/SEM Digital Marketing", key="sample_prompt_2", use_container_width=True):
                st.session_state.assessment["solution_description"] = "My solution manages SEO/SEM digital marketing campaigns, keyword bidding, and client conversion analytics."
                st.session_state.auto_trigger_search = True
                st.session_state.page = "Pre-Approval Assessment"
                st.session_state.assessment_step = 0
                st.rerun()
        with s_col3:
            if st.button("🔒 Cloud Cybersecurity", key="sample_prompt_3", use_container_width=True):
                st.session_state.assessment["solution_description"] = "My solution provides endpoint anti-malware, firewall protection, and automated threat detection for SME laptops."
                st.session_state.auto_trigger_search = True
                st.session_state.page = "Pre-Approval Assessment"
                st.session_state.assessment_step = 0
                st.rerun()

    st.markdown("<div class='portal-spacer-sm'></div>", unsafe_allow_html=True)

    col2, col3 = st.columns(2)
    with col2:
        render_feature_card(
            "STEP 2: CHECKLIST",
            "Category Checklist",
            "Complete category-specific functional requirements (Q1 to Q20+) extracted directly from the official guide.",
            icon="📋"
        )
        st.write("")
        if st.button("Review Checklist →", key="home_btn_checklist", type="primary", use_container_width=True):
            st.session_state.page = "Pre-Approval Assessment"
            st.session_state.assessment_step = 1
            st.rerun()

    with col3:
        render_feature_card(
            "STEP 3: PREREQUISITES",
            "Prerequisite Validation",
            "Verify incorporation age, financial stability ratios (positive equity, current ratio >= 1), InvoiceNow account status, and SME deployment benchmarks.",
            icon="🏢"
        )
        st.write("")
        if st.button("Start Assessment →", key="home_btn_prereq", type="primary", use_container_width=True):
            st.session_state.page = "Pre-Approval Assessment"
            st.session_state.assessment_step = 2
            st.rerun()

    st.markdown("<div class='portal-spacer-md'></div>", unsafe_allow_html=True)

    st.markdown("<h3 class='portal-section-heading'>The Pre-Approval Journey (Stage 2: Vendor Application)</h3>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown(
            """
            <div class="portal-spacer-sm">
                <span class="step-badge">
                    <span>🚀</span> STEP 4: SUBMISSION & VMP
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("<h4 class='portal-card-title'>🚀 Stage 2 Preparation & Formal VMP Submission</h4>", unsafe_allow_html=True)
        st.markdown(
            """
            <p class="portal-section-subtext">
                Once you clear Stage 1 Self-Assessment, review the official documentation guidelines to prepare your solution presentation deck, 
                pricing matrix, and customer proof before formally submitting via the Vendor Management Portal (VMP).
            </p>
            """,
            unsafe_allow_html=True
        )
        
        st4_col1, st4_col2 = st.columns(2)
        with st4_col1:
            st.link_button("📖 Read Stage 2 Guide ↗", STAGE_2_GUIDE_URL, type="primary", use_container_width=True)
        with st4_col2:
            st.link_button("🏛️ Launch VMP Portal ↗", VMP_PORTAL_URL, type="primary", use_container_width=True)

    render_footer_disclaimer()

# =========================================================
# PAGE 2: PRE-APPROVAL ASSESSMENT (4-STAGE FUNNEL)
# =========================================================

elif st.session_state.page == "Pre-Approval Assessment":
    render_brand_header(
        "Vendor Pre-Approval Assessment",
        subtitle="Complete your category discovery, functional checklist, eligibility validation, and application preparation in one unified workflow."
    )
    render_pre_approval_assessment()
    render_footer_disclaimer()

# =========================================================
# PAGE 3: ABOUT US
# =========================================================

elif st.session_state.page == "About Us":
    render_brand_header(
        "About This Project",
        subtitle="Background, problem statement, core deliverables, and public sector impact."
    )
    
    with st.container(border=True):
        st.markdown("""
        ### Executive Summary
        The **IMDA Pre-Approval Assistant** is an agentic, self-service copilot designed to bridge the operational gap between digital solution vendors (Infocomm Media - ICM vendors) and IMDA's Pre-Approval framework under the **SMEs Go Digital** programme.
        
        By automating eligibility pre-screening, category matching, and policy Q&A, this prototype transforms a tedious, document-heavy administrative workflow into an intuitive, guided digital experience.
        """)

    st.markdown("### 1. Operational Problem Statement")
    with st.container(border=True):
        st.markdown("""
        Vendors seeking IMDA pre-approval under the SMEs Go Digital programme encounter several operational friction points:
        - **Ambiguity in Domain Categorization:** Solutions with multi-faceted capabilities struggle to identify the correct pre-approval category upfront.
        - **Prerequisite Blindspots:** Vendors often apply before satisfying foundational criteria (e.g., 18-month incorporation, positive net equity, current ratio $\\ge 1$, or 5 SG SME deployments).
        - **Administrative Overhead:** IMDA officers spend extensive hours responding to recurring policy queries and reviewing non-compliant initial submissions.
        """)

    st.markdown("### 2. Core Functional Pillars (Structured 4-Stage Progression)")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        with st.container(border=True):
            st.markdown("#### 🎯 Guided 4-Stage Funnel")
            st.markdown("""
            - **Stage 1: Category Discovery:** Fast upfront check to ensure an official category exists before spending time on paperwork.
            - **Stage 2: Category Functional Checklist:** Mandatory requirement extraction and compliance evaluation.
            - **Stage 3: Prerequisite Validation:** Validates incorporation, financial health, track record, and InvoiceNow compliance.
            - **Stage 4: Review & Application Preparation:** Automatic gap detection, Copilot remediation, and VMP readiness guidance.
            """)
    with col_a2:
        with st.container(border=True):
            st.markdown("#### 🤖 Grounded AI Copilot")
            st.markdown("""
            - **Persistent Floating Modal:** Accessible from any page via the bottom-right `💬 Ask Copilot` widget.
            - **Context-Aware RAG:** Grounds responses directly in live IMDA pre-approval policy documents.
            - **Automated Gap Handover:** Transmits identified checklist gaps directly into the AI Copilot prompt pipeline for instant remediation advice.
            - **Submission Summary:** Formats structured submission records routed to reviewing public officers.
            """)

    st.markdown("### 3. Public Sector Digital Transformation Impact")
    with st.container(border=True):
        st.markdown("""
        - **Reduces Vendor Onboarding Cycle Time:** Speeds up pre-submission readiness checks from weeks to minutes.
        - **Minimizes Incomplete VMP Submissions:** Ensures only qualified, vetted solutions transition into the Vendor Management Portal (VMP).
        - **Fosters Responsible AI Adoption:** Implements input sanitization, heuristic defense, and authoritative source grounding.
        """)

    render_footer_disclaimer()

# =========================================================
# PAGE 4: METHODOLOGY & SYSTEM ARCHITECTURE
# =========================================================

elif st.session_state.page == "Methodology":
    render_brand_header(
        "Methodology & System Architecture",
        subtitle="Technical design, RAG pipeline, cybersecurity guardrails, and decoupled 6-module architecture."
    )
    
    with st.container(border=True):
        st.markdown("""
        ### Architectural Philosophy
        The **IMDA Pre-Approval Assistant** is built on a modular, service-oriented architecture designed to decouple policy schema definitions, web-scraped policy intelligence, generative AI reasoning, and presentation logic.
        
        The codebase is partitioned into six decoupled modules across `app.py`, `assessment_module.py`, `assessment_schemas.py`, `assessment_service.py`, `ui_components.py`, and `imda_knowledge.py`.
        """)

    st.markdown("### 1. Multi-Turn RAG Pipeline & Prompt Engineering")
    with st.container(border=True):
        st.markdown("""
        The conversational copilot uses **Google GenAI (`gemini-2.5-flash`)** orchestrated through a grounded Retrieval-Augmented Generation (RAG) architecture:
        - **Live Document Ingestion & Caching:** Pulls and caches markdown pages directly from the official portal (`https://preapproval-guide.imda.gov.sg/`) with TTL cache expiration to ensure compliance with the latest policy updates.
        - **XML Boundary Delimitation:** All untrusted user inputs and retrieved reference documents are enclosed within strict `<user_query>`, `<conversation_history>`, and `<context>` XML boundaries to prevent context contamination and jailbreaks.
        - **Multi-Turn Conversational Memory:** Preserves multi-turn state across user interactions, enabling vendors to ask follow-up questions regarding specific checklist items or financial ratios.
        - **Zero-Shot Semantic Matching:** Translates unstructured vendor solution descriptions into official IMDA categories using constrained JSON-like structural parsing.
        """)

    st.markdown("### 2. Cybersecurity & Prompt Injection Defenses")
    with st.container(border=True):
        st.markdown("""
        To safeguard public sector compliance integrity and prevent prompt tampering:
        - **Adversarial Regex Heuristics:** Evaluates incoming user inputs against multi-pattern jailbreak filters (e.g., `ignore previous instructions`, `system prompt`, `bypass guardrail`, `reveal API key`).
        - **XSS & Code Injection Sanitization:** Encodes angle brackets (`<`, `>`) and strips script tags (`<script>`, `javascript:`) before passing strings into the execution context.
        - **Prototype Passcode Gating:** Restricts prototype access via environment-managed passcodes verified against Streamlit Secrets.
        - **No Client-Side Credential Exposure:** All API keys (`GEMINI_API_KEY`) remain strictly server-side and are never serialized to the client browser.
        """)

    st.markdown("### 3. Modular Engineering Blueprint (6 Decoupled Modules)")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        with st.container(border=True):
            st.markdown("#### `app.py`")
            st.caption("Main Orchestration Engine (~200 lines)")
            st.markdown("Controls authentication gating, session state initialization, routing across primary pages (Home, Assessment, About, Methodology), and the persistent floating Copilot modal.")
        
        with st.container(border=True):
            st.markdown("#### `assessment_module.py`")
            st.caption("UI View Controller (~320 lines)")
            st.markdown("Encapsulates the presentation layer for all 4 assessment steps (Discovery, Functional Checklist, Prerequisite Tabs, and Review & Submission Summary) with interactive deep-linking.")

        with st.container(border=True):
            st.markdown("#### `assessment_schemas.py`")
            st.caption("Single Source of Truth Policy Schema (~110 lines)")
            st.markdown("Centralizes baseline criteria (Singapore incorporation, 18-month operation, positive net equity, current ratio $\\ge 1$, InvoiceNow status, and SME deployment benchmarks).")

    with col_m2:
        with st.container(border=True):
            st.markdown("#### `assessment_service.py`")
            st.caption("Scraping, Security & AI Matcher (~190 lines)")
            st.markdown("Handles remote markdown scraping from `preapproval-guide.imda.gov.sg`, question extraction regex, prompt injection sanitization, and Gemini-powered category recommendations.")

        with st.container(border=True):
            st.markdown("#### `ui_components.py`")
            st.caption("Design System & Brand Styling (~240 lines)")
            st.markdown("Implements the official SMEs Go Digital visual language (deep purple/magenta gradients, Singapore Government `.gov.sg` masthead drawer, scoped purple segmented stepper, and high-contrast button styling).")

        with st.container(border=True):
            st.markdown("#### `imda_knowledge.py`")
            st.caption("Grounded Knowledge Engine (~120 lines)")
            st.markdown("Manages portal constants, system prompt definitions, XML formatting for live RAG retrieval, and execution calls to the Gemini API client.")

    st.markdown("### 4. Stage 1 to Stage 2 Handover Workflow")
    with st.container(border=True):
        st.markdown("""
        1. **Stage 1: Vendor Self-Assessment:** Vendors self-screen eligibility upfront across category suitability, mandatory functional requirements, and corporate stability.
        2. **Gap Audit & Copilot Remediation:** Any unmet criteria are flagged as compliance gaps; vendors can click to pass gaps directly into the AI Copilot for remediation guidance.
        3. **Stage 2 Preparation & Submission:** Once compliant, the assistant generates a structured summary record and provides direct launch links to the **Vendor Management Portal (VMP)** and official submission guidelines.
        """)

    render_footer_disclaimer()

# =========================================================
# FLOATING ACTION CONTROLS
# =========================================================

st.markdown(
    """
    <div class="floating-action-bar">
        <a href="#page-top" class="floating-top-link">↑ Top</a>
    </div>
    """,
    unsafe_allow_html=True
)

if st.button("💬 Ask Copilot", key="floating_chat_button"):
    st.session_state.show_chat_dialog = True
    st.rerun()
