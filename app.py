"""
IMDA Pre-Approval Assistant — Application Orchestrator
Original Stable Version: Single-Passcode Gate, Zero Admin Roles, Full Navigation & CSS
"""

import streamlit as st

# 1. MUST BE THE VERY FIRST STREAMLIT CALL
st.set_page_config(
    page_title="IMDA Pre-Approval Assistant",
    page_icon="🇸🇬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Imports from modular architecture
from ui_components import load_custom_css
from assessment_module import render_pre_approval_assessment
from imda_knowledge import (
    MODEL_NAME,
    STAGE_2_GUIDE_URL,
    VMP_PORTAL_URL,
    CATEGORY_DIRECTORY_URL,
)

# 3. Apply Official Styling
load_custom_css()

# ---------------------------------------------------------
# Embedded Portal Header
# ---------------------------------------------------------
def render_portal_header():
    st.markdown(
        """
        <div class="portal-header-box" style="background: linear-gradient(135deg, #2b0b2e 0%, #4a154b 60%, #611f69 100%); color: #ffffff; padding: 24px 30px; border-radius: 12px; margin-bottom: 18px; box-shadow: 0 4px 14px rgba(43, 11, 46, 0.15);">
            <h1 style="color: #ffffff; font-size: 26px; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.3px;">🇸🇬 IMDA Pre-Approval Assistant</h1>
            <p style="color: #f1d5f5; font-size: 14px; margin: 0;">SMEs Go Digital Programme — Solution Pre-Qualification & Verification Portal</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "main_nav_tab" not in st.session_state:
    st.session_state.main_nav_tab = "🏠 Home / Overview"

# ---------------------------------------------------------
# View 1: Original Simple Password Gate
# ---------------------------------------------------------
if not st.session_state.authenticated:
    render_portal_header()
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        with st.container(border=True):
            st.markdown("### 🔒 Prototype Access Passcode")
            st.caption("This is a restricted proof-of-concept prototype. Please enter the passcode to access the assistant.")

            with st.form("simple_login_form"):
                passcode = st.text_input("Access Passcode", type="password")
                submitted = st.form_submit_button("Enter Assistant →", type="primary", use_container_width=True)

                if submitted:
                    expected_pwd = st.secrets.get("APP_PASSWORD", "bootcamp2026")
                    if passcode.strip() == expected_pwd.strip():
                        st.session_state.authenticated = True
                        st.rerun()
                    else:
                        st.error("Incorrect passcode. Please check credentials.")

            st.markdown("---")
            with st.expander("⚠️ IMPORTANT NOTICE — Proof-of-Concept Prototype", expanded=False):
                st.write(
                    """
                    This web application is developed as a proof-of-concept prototype. 
                    The information provided here is NOT intended for actual usage and should not be relied upon for making any decisions, 
                    especially those related to financial, legal, or healthcare matters.

                    Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. 
                    You assume full responsibility for how you use any generated output. 
                    Always consult with qualified professionals for accurate and personalised advice.
                    """
                )

    st.stop()

# ---------------------------------------------------------
# View 2: Authenticated Main Portal
# ---------------------------------------------------------
render_portal_header()

# Utility Bar: Active status and Logout
with st.container():
    col_info, col_logout = st.columns([6, 1.2])
    with col_info:
        st.markdown(
            "<span style='background:#f1f5f9; color:#334155; padding:4px 12px; border-radius:12px; font-size:12.5px; font-weight:600;'>"
            "👤 ICM Vendor Self-Assessment Portal"
            "</span>",
            unsafe_allow_html=True,
        )
    with col_logout:
        if st.button("Log Out ↪", key="btn_top_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Top Navigation Menu
# ---------------------------------------------------------
nav_options = [
    "🏠 Home / Overview",
    "📝 Pre-Approval Assessment",
    "ℹ️ About Us & Methodology"
]

selected_tab = st.radio(
    "Navigation Menu",
    nav_options,
    index=nav_options.index(st.session_state.main_nav_tab) if st.session_state.main_nav_tab in nav_options else 0,
    horizontal=True,
    label_visibility="collapsed"
)
st.session_state.main_nav_tab = selected_tab

st.markdown("<hr style='margin: 8px 0 20px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# =========================================================
# PAGE 1: HOME / STAGE 1 & STAGE 2 OVERVIEW
# =========================================================
if selected_tab == "🏠 Home / Overview":
    st.markdown("## 🧭 SMEs Go Digital Pre-Approval Framework Overview")
    st.caption("A structured 4-stage roadmap helping ICM technology vendors offer pre-approved digital solutions to Singapore SMEs.")

    tab_overview, tab_stage1, tab_stage2 = st.tabs([
        "📌 Programme Overview", 
        "1️⃣ Stage 1: Vendor Self-Assessment", 
        "2️⃣ Stage 2: Vendor Application"
    ])

    with tab_overview:
        with st.container(border=True):
            st.markdown("### What are Pre-Approved Solutions?")
            st.write(
                "Pre-Approved Solutions is an initiative under the **SMEs Go Digital** programme by the "
                "Infocomm Media Development Authority (IMDA). It curates pre-scoped, market-proven digital solutions "
                "so Singapore SMEs can adopt technology with confidence and receive up to 50% grant support through the "
                "Productivity Solutions Grant (PSG)."
            )

        col1, col2 = st.columns(2)
        with col1:
            with st.container(border=True):
                st.markdown("#### 1️⃣ Stage 1: Self-Assessment")
                st.write(
                    "- Verify business incorporation & financial ratios (Current Ratio ≥ 1).\n"
                    "- Confirm SME track record (minimum 3 deployments).\n"
                    "- Match product capabilities with an approved solution category.\n"
                    "- Complete the functional requirement checklist."
                )
                if st.button("Launch Self-Assessment Tool →", type="primary", use_container_width=True):
                    st.session_state.main_nav_tab = "📝 Pre-Approval Assessment"
                    st.rerun()

        with col2:
            with st.container(border=True):
                st.markdown("#### 2️⃣ Stage 2: Vendor Application")
                st.write(
                    "- Available only after satisfying Stage 1 readiness.\n"
                    "- Prepare solution architecture decks, standard pricing matrices, and customer invoices.\n"
                    "- Formally lodge application documents via the Vendor Management Portal (VMP).\n"
                    "- Undergo technical evaluation by IMDA officers."
                )
                st.link_button("View Stage 2 Documentation ↗", STAGE_2_GUIDE_URL, use_container_width=True)

    with tab_stage1:
        with st.container(border=True):
            st.markdown("### 1️⃣ Stage 1: Readiness & Feasibility Check")
            st.markdown(
                """
                Before applying in the portal, vendors must verify their readiness across **three core gates**:

                1. **Corporate & Financial Viability**:
                   - Business entity registered in Singapore with ACRA.
                   - Minimum 18 months of continuous operational history.
                   - Financially solvent with a **Current Ratio (Current Assets / Current Liabilities) ≥ 1**.

                2. **Track Record of Successful SME Deployments**:
                   - At least **3 distinct SME customer deployments** in Singapore.
                   - Invoices, contracts, or acceptance proof within the past 12 months.

                3. **Solution Eligibility & Technical Suitability**:
                   - Active InvoiceNow (Peppol) readiness.
                   - Cybersecurity hygiene certification (Cyber Essentials / Cyber Trust).
                   - Solution aligns 100% with mandatory criteria of an approved category.
                """
            )
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                st.link_button("Browse Official Category Directory ↗", CATEGORY_DIRECTORY_URL, use_container_width=True)
            with col_s2:
                if st.button("Begin Step-by-Step Self-Assessment →", type="primary", use_container_width=True):
                    st.session_state.main_nav_tab = "📝 Pre-Approval Assessment"
                    st.rerun()

    with tab_stage2:
        with st.container(border=True):
            st.markdown("### 2️⃣ Stage 2: Formal Application via VMP")
            st.markdown(
                """
                Once you meet Stage 1 criteria, you may prepare your submission packet for the **Vendor Management Portal (VMP)**:

                - **Document Checklist**:
                  - Latest ACRA BizFile profile (issued within 3 months).
                  - Full audited financial reports or CPA-certified balance sheets.
                  - Detailed solution deck specifying modular functional breakdown and system architecture.
                  - Standard bundled pricing package matrix for SME subscribers.
                  - 3 verifiable SME customer invoices and sign-off acceptance documentation.

                *Note: If your solution falls under an **unlisted category**, you cannot submit under Stage 2. Instead, use the self-assessment tool to lodge an Expression of Interest (EOI).*
                """
            )
            col_v1, col_v2 = st.columns(2)
            with col_v1:
                st.link_button("Launch Official VMP Portal ↗", VMP_PORTAL_URL, type="primary", use_container_width=True)
            with col_v2:
                st.link_button("Read Stage 2 Vendor Application Guide ↗", STAGE_2_GUIDE_URL, use_container_width=True)

# =========================================================
# PAGE 2: 4-STEP PRE-APPROVAL ASSESSMENT
# =========================================================
elif selected_tab == "📝 Pre-Approval Assessment":
    render_pre_approval_assessment()

# =========================================================
# PAGE 3: ABOUT US & METHODOLOGY (Capstone Requirement)
# =========================================================
elif selected_tab == "ℹ️ About Us & Methodology":
    st.markdown("## ℹ️ About Us & Technical Methodology")
    st.caption("Capstone Project Documentation for the AI Champions Bootcamp.")

    tab_about, tab_method, tab_governance = st.tabs([
        "👥 Project Background & Team", 
        "⚙️ Architecture & Methodology", 
        "🛡️ Safety, Guardrails & Governance"
    ])

    with tab_about:
        with st.container(border=True):
            st.markdown("### 👥 Project Background")
            st.write(
                "The **IMDA Pre-Approval Assistant** simplifies and accelerates the pre-qualification journey "
                "for Infocomm & Media (ICM) digital solution providers seeking pre-approval under the SMEs Go Digital programme. "
                "By guiding vendors through automated category discovery, prerequisite screening, and AI-grounded policy remediation, "
                "the platform eliminates ineligible applications and provides actionable compliance feedback."
            )

    with tab_method:
        with st.container(border=True):
            st.markdown("### 🏗️ Technical Architecture")
            st.markdown(
                """
                - **Primary LLM Engine**: `gemini-2.5-flash` via Google GenAI SDK.
                - **Decoupled 6-Module Design**:
                  1. `app.py`: Portal navigation, page layout, and application routing.
                  2. `ui_components.py`: Centralized UI styles and purple segmented stepper.
                  3. `assessment_module.py`: 4-step eligibility funnel and dynamic EOI handling.
                  4. `assessment_schemas.py`: Baseline prerequisite definitions and validation rules.
                  5. `assessment_service.py`: Category catalogue loader and semantic AI matching.
                  6. `imda_knowledge.py`: Live IMDA guide retrieval and grounded RAG Copilot.
                """
            )

    with tab_governance:
        with st.container(border=True):
            st.markdown("### 🛡️ AI Safety & Governance")
            st.markdown(
                """
                - **Prompt Injection Defense**: Regex pattern filtering blocks system prompts, jailbreaks, and command overrides.
                - **XML Boundary Delimiters**: Strict separation of context `<official_knowledge_base>` and `<vendor_context>`.
                """
            )
            st.warning(
                """
                **IMPORTANT NOTICE:** This web application is developed as a proof-of-concept prototype. 
                The information provided here is NOT intended for actual usage and should not be relied upon for making any decisions, 
                especially those related to financial, legal, or healthcare matters.

                Furthermore, please be aware that the LLM may generate inaccurate or incorrect information. 
                You assume full responsibility for how you use any generated output. 
                Always consult with qualified professionals for accurate and personalised advice.
                """
            )
