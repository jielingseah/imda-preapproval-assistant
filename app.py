"""
IMDA Pre-Approval Assistant — Application Orchestrator
Full-width portal layout with:
- Restored CSS styling from ui_components
- Home / Stage 1 & Stage 2 Guide Overview
- 4-Step Self-Assessment Funnel
- About Us & Methodology
- Officer Operations Console (Admin Role)
"""

from datetime import datetime
import pandas as pd
import streamlit as st

# 1. MUST BE FIRST
st.set_page_config(
    page_title="IMDA Pre-Approval Assistant",
    page_icon="🇸🇬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Imports from project modules
from ui_components import load_custom_css
from assessment_module import render_pre_approval_assessment
from imda_knowledge import (
    MODEL_NAME, 
    STAGE_2_GUIDE_URL, 
    VMP_PORTAL_URL, 
    CATEGORY_DIRECTORY_URL
)

# 3. Apply your official styling
load_custom_css()

# ---------------------------------------------------------
# Embedded Header Component & Role Badges
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
if "user_role" not in st.session_state:
    st.session_state.user_role = "User"
if "main_nav_tab" not in st.session_state:
    st.session_state.main_nav_tab = "🏠 Home / Overview"
if "all_submissions" not in st.session_state:
    st.session_state.all_submissions = []
if "intake_window_open" not in st.session_state:
    st.session_state.intake_window_open = True
if "allow_unlisted_eoi" not in st.session_state:
    st.session_state.allow_unlisted_eoi = True
if "cache_ttl_hours" not in st.session_state:
    st.session_state.cache_ttl_hours = 6
if "last_cache_sync" not in st.session_state:
    st.session_state.last_cache_sync = datetime.now().strftime("%Y-%m-%d %H:%M SGT")

# ---------------------------------------------------------
# View 1: Gated Authentication Screen
# ---------------------------------------------------------
if not st.session_state.authenticated:
    render_portal_header()
    st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)

    _, col_center, _ = st.columns([1, 2, 1])
    with col_center:
        with st.container(border=True):
            st.markdown("### 🔐 SMEs Go Digital Portal Authentication")
            st.caption("Select your role and enter the prototype authorization passcode.")

            with st.form("login_form"):
                selected_role = st.radio(
                    "Select Access Role:",
                    ["Vendor / ICM Applicant (User)", "IMDA Reviewing Officer (Admin)"],
                    index=0,
                    help="Switch between public vendor self-assessment and internal officer controls."
                )

                passcode = st.text_input("Prototype Authorization Passcode", type="password")
                submitted = st.form_submit_button("Authenticate & Access →", type="primary", use_container_width=True)

                if submitted:
                    correct_pw = st.secrets.get("APP_PASSWORD", "demo123")
                    if passcode.strip() == correct_pw.strip():
                        st.session_state.authenticated = True
                        st.session_state.user_role = "Admin" if "Admin" in selected_role else "User"
                        st.rerun()
                    else:
                        st.error("Invalid authorization passcode. Please check your credential.")

            st.info(
                "💡 **Prototype Evaluation Note:** Both roles use the same prototype password. "
                "Select **Vendor** to test the self-assessment funnel, or **Admin** to access officer operations."
            )

    st.stop()

# ---------------------------------------------------------
# View 2: Authenticated Main Portal
# ---------------------------------------------------------
render_portal_header()

# Role Header and Logout Bar
with st.container():
    col_info, col_logout = st.columns([6, 1.2])
    with col_info:
        if st.session_state.user_role == "Admin":
            st.markdown(
                "<span style='background:#ede9fe; color:#5b21b6; padding:4px 12px; border-radius:12px; font-size:12.5px; font-weight:600;'>"
                "🛡️ Mode: IMDA Reviewing Officer (Admin)"
                "</span>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<span style='background:#f1f5f9; color:#334155; padding:4px 12px; border-radius:12px; font-size:12.5px; font-weight:600;'>"
                "👤 Mode: ICM Vendor Applicant"
                "</span>",
                unsafe_allow_html=True
            )
    with col_logout:
        if st.button("Log Out ↪", key="btn_top_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_role = "User"
            st.rerun()

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Navigation Bar
# ---------------------------------------------------------
nav_options = ["🏠 Home / Overview", "📝 Pre-Approval Assessment", "ℹ️ About Us & Methodology"]
if st.session_state.user_role == "Admin":
    nav_options.append("⚙️ Officer Operations Console")

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
# PAGE 3: ABOUT US & METHODOLOGY (Capstone Rubric)
# =========================================================
elif selected_tab == "ℹ️ About Us & Methodology":
    st.markdown("## ℹ️ About Us & Technical Methodology")
    st.caption("Capstone Project Documentation for the AI Champions Bootcamp & Public Sector GenAI Track.")

    tab_about, tab_method, tab_governance = st.tabs([
        "👥 Project Background & Team", 
        "⚙️ Architecture & Methodology", 
        "🛡️ Safety, Guardrails & Governance"
    ])

    with tab_about:
        with st.container(border=True):
            st.markdown("### 👥 Project Background")
            st.write(
                "The **IMDA Pre-Approval Assistant** addresses the operational complexity experienced by ICM digital solution "
                "providers attempting to navigate the SMEs Go Digital pre-approval framework. By automating category discovery, "
                "cross-referencing baseline prerequisites, and providing an AI-guided policy copilot, the assistant minimizes manual "
                "review cycles and eliminates non-compliant submissions before they reach reviewing officers."
            )

    with tab_method:
        with st.container(border=True):
            st.markdown("### 🏗️ Technical Architecture")
            st.markdown(
                """
                - **Primary LLM Engine**: `gemini-2.5-flash` via the official Google GenAI SDK.
                - **Decoupled 6-File Modular Architecture**:
                  1. `app.py`: Full-width portal routing, navigation, and state orchestration.
                  2. `ui_components.py`: Centralized UI tokens, styles, and segmented stepper.
                  3. `assessment_module.py`: Interactive 4-step assessment funnel and dynamic EOI logic.
                  4. `assessment_schemas.py`: Declarative baseline prerequisite definitions and compliance criteria.
                  5. `assessment_service.py`: Heuristic validation, category directory scraper, and embedding matching.
                  6. `imda_knowledge.py`: Real-time guide chunk ingestion and multi-turn grounded RAG Copilot.
                """
            )

    with tab_governance:
        with st.container(border=True):
            st.markdown("### 🛡️ AI Safety, Prompt Injection Defense & Governance")
            st.markdown(
                """
                - **Heuristic Pattern Defense**: User inputs are scanned via regex filters for prompt injection, system overrides, and exfiltration attacks.
                - **Prompt Boundary Scaffolding**: Enforces clear XML delineation (`<official_knowledge_base>`, `<vendor_context>`) to eliminate instruction-mixing vulnerabilities.
                - **Prototype Governance Copy**:
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

# =========================================================
# PAGE 4: OFFICER OPERATIONS CONSOLE (ADMIN ONLY)
# =========================================================
elif selected_tab == "⚙️ Officer Operations Console" and st.session_state.user_role == "Admin":
    st.markdown("### ⚙️ IMDA Officer Operations & Ingestion Console")
    st.caption("Manage ingestion schedules, knowledge cache invalidation, category intake windows, and review vendor submissions.")

    tab_ops, tab_submissions, tab_telemetry = st.tabs([
        "🔄 Ingestion & Scheduler", 
        "📋 Vendor Submissions Registry", 
        "🛡️ LLM Guardrails & Runtime"
    ])

    with tab_ops:
        with st.container(border=True):
            st.markdown("#### 🕒 Official Guide Ingestion & Scraper Schedule")
            st.write(
                "The RAG knowledge base dynamically parses official documentation from "
                "`preapproval-guide.imda.gov.sg`. Configure sync intervals or force an immediate re-scrape."
            )
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.cache_ttl_hours = st.selectbox(
                    "Automated Ingestion Refresh Interval (Scheduler)",
                    [1, 6, 12, 24],
                    index=1,
                    format_func=lambda x: f"Every {x} hour(s)"
                )
                st.caption(f"Last automated synchronization completed: `{st.session_state.last_cache_sync}`")

            with col2:
                st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
                if st.button("⚡ Force Immediate Manual Ingestion Sync", type="primary", use_container_width=True):
                    with st.spinner("Flushing cache and re-synchronizing knowledge chunks..."):
                        st.cache_data.clear()
                        st.session_state.last_cache_sync = datetime.now().strftime("%Y-%m-%d %H:%M SGT")
                    st.success("Ingestion successful! In-memory knowledge cache refreshed.")
                    st.rerun()

        with st.container(border=True):
            st.markdown("#### 🚪 SMEs Go Digital Intake Window Governance")
            c1, c2 = st.columns(2)
            with c1:
                st.session_state.intake_window_open = st.toggle(
                    "Open for Stage 1 Category Submissions", 
                    value=st.session_state.intake_window_open
                )
                status_text = "🟢 ACTIVE / ACCEPTING SUBMISSIONS" if st.session_state.intake_window_open else "🔴 CLOSED"
                st.caption(f"Current Intake Status: **{status_text}**")
            with c2:
                st.session_state.allow_unlisted_eoi = st.toggle(
                    "Accept Expressions of Interest (EOI) for Unlisted Categories", 
                    value=st.session_state.allow_unlisted_eoi
                )
                st.caption("Permits vendors to submit company profiles even if no solution category matches.")

    with tab_submissions:
        st.markdown("#### 📥 Logged Vendor Intake & Self-Assessment Records")
        records = st.session_state.get("all_submissions", [])

        if not records:
            st.info("No vendor submissions have been recorded in this active session yet.")
            st.caption("When a vendor completes Step 4, their submission record, gaps, and notes will appear here.")
        else:
            df = pd.DataFrame(records)
            st.dataframe(df, use_container_width=True)

            csv_data = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Submission Registry to CSV",
                data=csv_data,
                file_name=f"imda_vendor_submissions_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                type="primary"
            )

    with tab_telemetry:
        with st.container(border=True):
            st.markdown("#### 🤖 Model Configuration")
            st.markdown("- **Primary LLM:** `gemini-2.5-flash` (Google GenAI)")
            st.markdown("- **Prompt Scaffolding:** XML-delimited (`<official_knowledge_base>`, `<vendor_context>`)")
            st.markdown("- **Input Defense:** Regex-based heuristic pattern defense (Jailbreak / Injection interception)")
            st.markdown(f"- **Officer Notification Route:** `{st.secrets.get('OFFICER_REVIEW_EMAIL', 'seah_jie_ling@imda.gov.sg')}`")
