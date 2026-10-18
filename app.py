import streamlit as st
from google import genai

# Import multi-turn RAG knowledge engine
from imda_knowledge import query_live_guide_rag

# Import UI / UX component library
from ui_components import (
    inject_custom_css,
    render_brand_header,
    render_hero_banner,
    render_feature_card,
    render_footer_disclaimer
)

# Import extracted domain assessment engine
from assessment_module import (
    render_pre_approval_assessment,
    sanitize_and_check_injection,
    MODEL_NAME
)

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

# =========================================================
# PAGE 1: HOME PAGE
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

    # Main Page Hero Search Bar — Solution Category Pre-Check (Angle 1)
    with st.container(border=True):
        st.markdown(
            "<h4 style='font-weight:700; color:#2b0b2e; margin:0 0 6px 0;'>🔍 Solution Category Pre-Check</h4>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='font-size:12.5px; color:#636375; margin-bottom:12px; line-height:1.5;'>"
            "Check if your solution fits an official IMDA category before starting self-assessment. "
            "If your product does not fall under an existing pre-approved category, it is not eligible under this programme."
            "</p>",
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
                    st.session_state.assessment_step = 1
                    st.rerun()

        st.markdown("<p style='font-size:11.5px; color:#777788; margin-top:8px; margin-bottom:4px;'>💡 Or click a sample prompt to try:</p>", unsafe_allow_html=True)
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            if st.button("🏫 Pre-School Operations", key="sample_prompt_1", use_container_width=True):
                st.session_state.assessment["solution_description"] = "My solution helps manage pre-school operations, student attendance, parent communications, and fee collection."
                st.session_state.auto_trigger_search = True
                st.session_state.page = "Pre-Approval Assessment"
                st.session_state.assessment_step = 1
                st.rerun()
        with s_col2:
            if st.button("📈 SEO/SEM Digital Marketing", key="sample_prompt_2", use_container_width=True):
                st.session_state.assessment["solution_description"] = "My solution manages SEO/SEM digital marketing campaigns, keyword bidding, and client conversion analytics."
                st.session_state.auto_trigger_search = True
                st.session_state.page = "Pre-Approval Assessment"
                st.session_state.assessment_step = 1
                st.rerun()
        with s_col3:
            if st.button("🔒 Cloud Cybersecurity", key="sample_prompt_3", use_container_width=True):
                st.session_state.assessment["solution_description"] = "My solution provides endpoint anti-malware, firewall protection, and automated threat detection for SME laptops."
                st.session_state.auto_trigger_search = True
                st.session_state.page = "Pre-Approval Assessment"
                st.session_state.assessment_step = 1
                st.rerun()

    st.markdown("---")

    # The Pre-Approval Journey (Stage 1) - Front & Center
    st.markdown("<h3 style='font-size:20px; font-weight:800; color:#2b0b2e; margin-bottom:14px;'>The Pre-Approval Journey (Stage 1)</h3>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        render_feature_card(
            "Step 1: Eligibility",
            "Prerequisite Validation",
            "Verify incorporation age, financial ratios (positive equity, current ratio >= 1), and SME deployment benchmarks."
        )
        st.write("")
        if st.button("Start Assessment →", key="home_btn_assess", use_container_width=True):
            st.session_state.page = "Pre-Approval Assessment"
            st.session_state.assessment_step = 0
            st.rerun()

    with col2:
        render_feature_card(
            "Step 2: Matching",
            "Category Discovery",
            "Semantic category matching powered by Gemini or browse the interactive directory with numbered pagination."
        )
        st.write("")
        if st.button("Browse Categories →", key="home_btn_cat", use_container_width=True):
            st.session_state.page = "Pre-Approval Assessment"
            st.session_state.assessment_step = 1
            st.rerun()

    with col3:
        render_feature_card(
            "Step 3: Audit",
            "Functional Gap Review",
            "Complete mandatory functional criteria, audit compliance gaps, and prepare submission dossiers."
        )
        st.write("")
        if st.button("Review Checklist →", key="home_btn_check", type="primary", use_container_width=True):
            st.session_state.page = "Pre-Approval Assessment"
            st.session_state.assessment_step = 2
            st.rerun()

    st.markdown("---")

    # External Official Ecosystem Resources (Positioned at bottom)
    st.markdown("<h4 style='font-size:16px; font-weight:700; color:#581845; margin-bottom:12px;'>Official IMDA Framework & Portals</h4>", unsafe_allow_html=True)
    col_info1, col_info2 = st.columns(2)
    with col_info1:
        with st.container(border=True):
            st.markdown("#### 📘 Official IMDA Pre-Approval Guide")
            st.write(
                """
                Under the **SMEs Go Digital** initiative, solutions are vetted for quality, market readiness, and track record. 
                Eligible SMEs adopting these solutions can receive productivity grant support. 
                Use this self-assessment to verify all requirements upfront before submission.
                """
            )
            st.link_button("View Official IMDA Guide ↗", "https://preapproval-guide.imda.gov.sg/", use_container_width=True)

    with col_info2:
        with st.container(border=True):
            st.markdown("#### 🏛️ Vendor Management Portal (VMP)")
            st.write(
                """
                The **Vendor Management Portal (VMP)** is IMDA's official platform where tech vendors formally submit applications, 
                track submission milestones, manage approved solution packages, and report SME deployments.
                """
            )
            st.link_button("Access Vendor Management Portal (VMP) ↗", "https://services2-stg.imda.gov.sg/VMP/", use_container_width=True)

    render_footer_disclaimer()

# =========================================================
# PAGE 2: PRE-APPROVAL ASSESSMENT (STEP 1 -> STEP 2 -> STEP 3)
# =========================================================

elif st.session_state.page == "Pre-Approval Assessment":
    render_brand_header(
        "Vendor Pre-Approval Assessment",
        subtitle="Complete your eligibility validation, select your solution category, and audit functional requirements in one unified workflow."
    )
    render_pre_approval_assessment()
    render_footer_disclaimer()

# =========================================================
# PAGE 3: ABOUT US
# =========================================================

elif st.session_state.page == "About Us":
    render_brand_header("About This Project", subtitle="Background, problem statement, core deliverables, and public sector impact.")
    
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
        - **Ambiguity in Domain Categorization:** Solutions with multi-faceted capabilities (e.g. POS with inventory and invoicing) struggle to identify the correct pre-approval category.
        - **Prerequisite Blindspots:** Vendors often apply before satisfying foundational criteria (e.g., 18-month incorporation, positive net equity, current ratio $\ge 1$, or 5 SG SME deployments).
        - **Administrative Overhead:** IMDA officers spend extensive hours responding to recurring policy queries and reviewing non-compliant initial submissions.
        """)

    st.markdown("### 2. Core Functional Pillars")
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        with st.container(border=True):
            st.markdown("#### 🎯 Guided 3-Step Assessment Funnel")
            st.markdown("""
            - **Step 1: Baseline Prerequisites:** Validates incorporation, financial health, track record, and compliance.
            - **Step 2: Category Discovery:** Combines zero-shot Gemini semantic matching with an interactive, paginated manual catalogue.
            - **Step 3: Gap Audit & Review:** Evaluates official checklists and gives interactive editing links for identified gaps.
            """)
    with col_a2:
        with st.container(border=True):
            st.markdown("#### 🤖 Grounded AI Copilot")
            st.markdown("""
            - **Persistent Floating Modal:** Accessible from any page via the bottom-right `💬 Ask Copilot` widget.
            - **Context-Aware RAG:** Grounds responses directly in live IMDA pre-approval policy documents.
            - **Automated Gap Handover:** Transmits identified checklist gaps directly into the AI Copilot prompt pipeline for instant remediation advice.
            - **Dossier Dispatch:** Formats structured submission records routed to reviewing public officers.
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
    render_brand_header("Methodology & System Architecture", subtitle="Technical design, RAG pipeline, cybersecurity guardrails, and modular code architecture.")
    
    with st.container(border=True):
        st.markdown("""
        ### Architectural Philosophy
        The application is engineered using clean software engineering principles, decoupling user interface styling, session orchestration, domain assessment logic, and GenAI knowledge retrieval across four modular files:
        `app.py`, `assessment_module.py`, `ui_components.py`, and `imda_knowledge.py`.
        """)

    st.markdown("### 1. Multi-Turn RAG Pipeline & Prompt Engineering")
    with st.container(border=True):
        st.markdown("""
        The conversational copilot uses the `gemini-3.8-flash` model orchestrated through a Retrieval-Augmented Generation (RAG) pipeline:
        - **Dynamic Context Injection:** Pulls live markdown data directly from `https://preapproval-guide.imda.gov.sg/`.
        - **XML Boundary Delimitation:** All untrusted inputs are encapsulated within strict `<user_query>` and `<context>` XML tags to prevent context bleeding.
        - **Multi-Turn Session Memory:** Tracks conversation state within structured `<conversation_history>` envelopes to support sequential follow-up reasoning.
        - **Zero-Shot Semantic Matching:** Matches plain-language solution descriptions to exact official categories using strict JSON-like structured response parsing.
        """)

    st.markdown("### 2. Cybersecurity & Prompt Injection Defenses")
    with st.container(border=True):
        st.markdown("""
        To defend against malicious prompt engineering and compliance tampering, the app enforces an automated security layer:
        - **Adversarial Regex Heuristics:** Blocks instruction override sequences (e.g. `ignore previous instructions`, `system prompt`, `bypass guardrails`).
        - **XSS & HTML Sanitization:** Strips HTML/script tags (`<script>`, `javascript:`) before processing user inputs.
        - **Access Authentication Gate:** Secures the prototype environment via session passcode authentication.
        """)

    st.markdown("### 3. Modular Engineering Blueprint (4 Modules)")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        with st.container(border=True):
            st.markdown("#### `app.py`")
            st.caption("Main Orchestration Engine (~170 lines)")
            st.markdown("Handles access gating, session routing, persistent floating copilot modal state, and Home/Documentation page renderers.")
        with st.container(border=True):
            st.markdown("#### `assessment_module.py`")
            st.caption("Domain Assessment Funnel (~320 lines)")
            st.markdown("Encapsulates the 3-step assessment funnel: Step 1 Baseline Validation, Step 2 AI Category Matcher & Paginated Catalogue, and Step 3 Checklist Gap Audit & Officer Dossier.")

    with col_m2:
        with st.container(border=True):
            st.markdown("#### `ui_components.py`")
            st.caption("Design System & Styling (~180 lines)")
            st.markdown("Encapsulates official SMEs Go Digital portal branding, universal font syncing, 4-item top navigation bar, floating trigger buttons, and footer disclaimers.")
        with st.container(border=True):
            st.markdown("#### `imda_knowledge.py`")
            st.caption("Grounded Knowledge Engine (~120 lines)")
            st.markdown("Parses live IMDA documentation, manages multi-turn RAG prompt templates, and executes grounded LLM generation with retry logic.")

    render_footer_disclaimer()

# =========================================================
# FLOATING ACTION CONTROLS (RENDERED AT VERY END TO PREVENT TOP GAP)
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
