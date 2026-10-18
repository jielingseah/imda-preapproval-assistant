import streamlit as st
from google import genai
import pandas as pd

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

# Injected globally so both Member of Public and Admin share the exact same CSS styling
inject_custom_css()

# Anchor point for instant return to top
st.markdown('<div id="page-top"></div>', unsafe_allow_html=True)

# =========================================================
# ACCESS CONTROL (Strict Secrets Authentication + Role Toggle)
# =========================================================

def check_password():
    """Gives access only if correct password configured in Streamlit Secrets is provided."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = "Member of Public"

    if st.session_state.authenticated:
        return True

    # Official SG Masthead for login screen
    st.markdown(
        """
        <details class="sg-masthead">
            <summary class="sg-masthead-summary">
                <span class="sg-masthead-crest">🇸🇬</span> 
                <span>A Singapore Government Agency Website</span> 
                <span class="sg-masthead-trigger">How to identify ▾</span>
            </summary>
            <div class="sg-masthead-drawer">
                <div class="sg-masthead-col">
                    <span class="sg-masthead-icon">🏛️</span>
                    <div>
                        <div class="sg-masthead-text-title">Official website links end with .gov.sg</div>
                        <p class="sg-masthead-text-desc">
                            Government agencies communicate via .gov.sg websites. 
                            <a href="https://www.gov.sg/trusted-sites#govsites" target="_blank" rel="noopener noreferrer">Trusted websites ↗</a>
                        </p>
                    </div>
                </div>
                <div class="sg-masthead-col">
                    <span class="sg-masthead-icon">🔒</span>
                    <div>
                        <div class="sg-masthead-text-title">Secure websites use HTTPS</div>
                        <p class="sg-masthead-text-desc">
                            Look for a <strong>lock (🔒)</strong> or https:// as an added precaution.
                        </p>
                    </div>
                </div>
            </div>
        </details>
        """,
        unsafe_allow_html=True
    )

    # Branded Header Lockup
    st.markdown(
        """
        <div style="height: 44px; display: flex; align-items: center; gap: 10px; margin-bottom: 24px; user-select: none;">
            <div style="line-height: 1;">
                <span style="font-size: 24px; font-weight: 800; color: #581845; letter-spacing: -0.5px;">SMEs</span><span style="font-size: 24px; font-weight: 800; color: #d8232a; letter-spacing: -0.5px;">godigital</span>
            </div>
            <div style="height: 20px; width: 1.5px; background-color: #d0c4d8;"></div>
            <div style="line-height: 1.15;">
                <span style="font-size: 15px; font-weight: 800; color: #581845; letter-spacing: -0.2px;">Pre-Approval Assistant</span>
                <span style="display: block; font-size: 10px; font-weight: 700; color: #7a1d5a; text-transform: uppercase; letter-spacing: 0.5px;">IMDA Pilot</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    login_col1, _, _ = st.columns([1.8, 1.2, 1.0])
    with login_col1:
        with st.container(border=True):
            st.markdown(
                """
                <span class="step-badge">
                    <span>🔒</span> AUTHORIZED ACCESS ONLY
                </span>
                <h3 style="font-size: 18px; font-weight: 800; color: #2b0b2e; margin-top: 6px; margin-bottom: 4px;">
                    Prototype Access Gate
                </h3>
                <p style="font-size: 13px; color: #636375; line-height: 1.5; margin-bottom: 16px;">
                    This is an authorized demonstration prototype under the IMDA SMEs Go Digital pilot. Please select your role and enter the passcode provided in LaunchPad.
                </p>
                """,
                unsafe_allow_html=True
            )

            # Role Toggle
            selected_role = st.radio(
                "Access Role",
                ["Member of Public", "Admin"],
                index=0,
                horizontal=True,
                key="login_role_toggle"
            )

            pwd_input = st.text_input("Access Passcode", type="password", key="login_passcode", placeholder="Enter passcode...")
            st.markdown("<div style='margin-bottom: 10px;'></div>", unsafe_allow_html=True)

            if st.button("Enter Assistant →", type="primary", use_container_width=True):
                configured_pwd = str(st.secrets.get("APP_PASSWORD", "")).strip().lower()
                user_entered = pwd_input.strip().lower() if pwd_input else ""

                if not configured_pwd:
                    st.error("Authentication configuration error: 'APP_PASSWORD' is not set in Streamlit Secrets.")
                elif user_entered == configured_pwd:
                    st.session_state.authenticated = True
                    st.session_state.user_role = selected_role
                    st.rerun()
                else:
                    st.error("Incorrect passcode. Please check your credentials.")

    render_footer_disclaimer()
    return False

if not check_password():
    st.stop()

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
# ROLE ROUTING: ADMIN CONSOLE
# =========================================================

if st.session_state.get("user_role") == "Admin":
    # High-contrast Branded Header with scoped CSS override to prevent global dark font bleed
    st.markdown(
        """
        <style>
            #admin-header-card, #admin-header-card * {
                color: #ffffff !important;
            }
            #admin-header-card h2 {
                color: #ffffff !important;
                font-size: 24px !important;
                font-weight: 800 !important;
                margin: 8px 0 6px 0 !important;
                letter-spacing: -0.3px !important;
            }
            #admin-header-card p {
                color: #f8fafc !important;
                font-size: 13.5px !important;
                margin: 0 !important;
                opacity: 0.95 !important;
            }
            #admin-header-card .admin-badge {
                background: rgba(255, 255, 255, 0.2) !important;
                color: #ffffff !important;
                font-size: 11px !important;
                font-weight: 800 !important;
                padding: 4px 10px !important;
                border-radius: 6px !important;
                display: inline-block !important;
                letter-spacing: 0.8px !important;
            }
        </style>

        <div id="admin-header-card" style="background: linear-gradient(135deg, #2b0b2e 0%, #4a154b 60%, #611f69 100%); padding: 24px 30px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(43, 11, 46, 0.25);">
            <span class="admin-badge">SYSTEM ADMINISTRATOR</span>
            <h2>🛡️ IMDA Officer Operations & Pipeline Console</h2>
            <p>Manage daily knowledge harvesting automation, category intake governance, and audit vendor submissions.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Top Utility Bar for Admin
    admin_bar_col1, admin_bar_col2 = st.columns([5, 1.2])
    with admin_bar_col1:
        st.markdown(
            """
            <span class="step-badge">
                <span>🛡️</span> AUTHENTICATED AS: IMDA OFFICER (ADMIN)
            </span>
            """,
            unsafe_allow_html=True
        )
    with admin_bar_col2:
        if st.button("Log Out ↪", key="btn_admin_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

    tab_pipeline, tab_knowledge, tab_submissions = st.tabs([
        "🕒 Automated Ingestion Scheduler", 
        "📚 Knowledge Base & Endpoints", 
        "📋 Submissions & Intake Governance"
    ])

    # TAB 1: GITHUB ACTIONS SCHEDULER & PIPELINE
    with tab_pipeline:
        with st.container(border=True):
            st.markdown(
                """
                <div class="portal-spacer-sm">
                    <span class="step-badge">
                        <span>🤖</span> SCHEDULED GITHUB ACTIONS DAEMON
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("<h4 class='portal-card-title'>Daily Headless Ingestion Daemon (<code>daily_refresh.yml</code>)</h4>", unsafe_allow_html=True)
            st.markdown(
                """
                <p class="portal-section-subtext">
                    Knowledge is automatically crawled from <code>https://preapproval-guide.imda.gov.sg</code> 
                    via a headless GitHub Actions runner and committed directly to repository version control.
                </p>
                """,
                unsafe_allow_html=True
            )
            
            p_col1, p_col2 = st.columns(2)
            with p_col1:
                st.markdown("- **Cron Trigger:** `0 19 * * *` (Daily at 03:00 SGT)")
                st.markdown("- **Target Serialized Output:** `data/knowledge_index.json`")
                st.markdown("- **Runner Environment:** `ubuntu-latest` (Python 3.11)")
            with p_col2:
                st.markdown("- **Permissions:** `contents: write` (Bot Commits)")
                st.markdown("- **Execution Script:** `python imda_knowledge.py`")
                st.markdown("- **Scheduler Health:** `🟢 Active / Scheduled`")

            st.markdown("---")
            st.markdown("##### 📄 Workflow Pipeline Specification")
            st.code("""name: Daily IMDA Knowledge Refresh

on:
  schedule:
    - cron: "0 19 * * *"
  workflow_dispatch:

permissions:
  contents: write

jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: pip install requests streamlit google-genai
      - name: Refresh knowledge index
        run: python imda_knowledge.py
      - name: Commit changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add data/knowledge_index.json
          if ! git diff --cached --quiet; then
            git commit -m "Refresh IMDA knowledge base"
            git push
          fi""", language="yaml")

            if st.button("⚡ Force Immediate Manual Cache Invalidation", type="primary"):
                st.cache_data.clear()
                st.success("Streamlit knowledge cache cleared! Next user query will read fresh source chunks.")

    # TAB 2: KNOWLEDGE BASE ENDPOINTS
    with tab_knowledge:
        with st.container(border=True):
            st.markdown("<h4 class='portal-card-title'>📚 Grounded Official Document Endpoints</h4>", unsafe_allow_html=True)
            st.write("Active official endpoints ingested into the RAG knowledge pool:")
            st.markdown("- **Stage 1 Self-Assessment Guide:** `https://preapproval-guide.imda.gov.sg/pre-approval-guide/stage-1-vendor-self-assessment.md`")
            st.markdown("- **Stage 2 Vendor Application Guide:** `https://preapproval-guide.imda.gov.sg/pre-approval-guide/stage-2-vendor-application.md`")
            st.markdown("- **Pre-Approved Solution Categories Directory:** `https://preapproval-guide.imda.gov.sg/pre-approval-guide/stage-1-vendor-self-assessment/identify-suitable-solution-category.md`")
            st.info("ℹ️ These files are pre-chunked with XML boundaries (`<context>`, `<applicant_state>`, `<user_query>`) before embedding.")

    # TAB 3: SUBMISSIONS & INTAKE GOVERNANCE
    with tab_submissions:
        with st.container(border=True):
            st.markdown("<h4 class='portal-card-title'>🚪 Category Intake Governance</h4>", unsafe_allow_html=True)
            st.caption("Operational controls for intake cycles in active runtime session:")
            st.toggle("Accept New Vendor Stage 1 Self-Assessments", value=True, key="admin_intake_toggle")
            st.toggle("Permit Expressions of Interest (EOI) for Unlisted Categories", value=True, key="admin_eoi_toggle")

        with st.container(border=True):
            st.markdown("<h4 class='portal-card-title'>📥 Logged Session Submissions</h4>", unsafe_allow_html=True)
            submissions = st.session_state.get("all_submissions", [])
            if not submissions:
                st.info("No vendor assessment submissions recorded in current active session memory.")
                st.caption("When a vendor finishes Step 4 in the Public view, their company profile, website, and gaps will appear here.")
            else:
                df = pd.DataFrame(submissions)
                st.dataframe(df, use_container_width=True)

    render_footer_disclaimer()
    st.stop()  # Admin execution halts here, keeping Member of Public completely isolated below

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
        subtitle="Project scope, objectives, official data sources, and system capabilities.",
        badge="Governance & Scope"
    )

    with st.container(border=True):
        st.markdown("### 📌 1. Project Scope & Background")
        st.markdown("""
        The **IMDA Pre-Approval Assistant** is an agentic, self-service copilot developed under the **SMEs Go Digital** programme. 
        It bridges the operational gap between digital solution providers (Infocomm Media / ICM vendors) and IMDA's rigorous pre-approval accreditation framework.
        
        The scope of this prototype encompasses:
        - Upfront automated qualification against official baseline corporate and financial criteria.
        - Semantic classification of unstructured vendor solution offerings into official pre-approved categories.
        - Automated category functional checklist verification and gap analysis.
        - Conversational RAG guidance grounded in live Singapore government policy documentation.
        """)

    with st.container(border=True):
        st.markdown("### 🎯 2. Core Objectives")
        col_obj1, col_obj2 = st.columns(2)
        with col_obj1:
            st.markdown("""
            - **Accelerate Onboarding Velocity:** Compress vendor self-assessment readiness cycles from several weeks to minutes.
            - **Eliminate Incomplete VMP Submissions:** Ensure only qualified, vetted applicants transition to formal Vendor Management Portal (VMP) submission.
            """)
        with col_obj2:
            st.markdown("""
            - **Reduce Administrative Drag:** Mitigate public sector officer overhead spent answering recurring baseline qualification queries.
            - **Demonstrate Responsible AI:** Maintain zero hallucination risks through grounded RAG boundaries and prompt injection heuristics.
            """)

    with st.container(border=True):
        st.markdown("### 🌐 3. Authoritative Data Sources")
        st.markdown("""
        The application ingests zero synthetic or unverified data. All knowledge bases are synchronized directly from official Singapore Government web endpoints:
        - **IMDA Stage 1 Self-Assessment Guide:** `https://preapproval-guide.imda.gov.sg/pre-approval-guide/stage-1-vendor-self-assessment.md`
        - **IMDA Stage 2 Vendor Application Guide:** `https://preapproval-guide.imda.gov.sg/pre-approval-guide/stage-2-vendor-application.md`
        - **Pre-Approved Solution Categories Directory:** `https://preapproval-guide.imda.gov.sg/pre-approval-guide/stage-1-vendor-self-assessment/identify-suitable-solution-category.md`
        - **Official SG Masthead Security Specifications:** Trust guidelines via `gov.sg/trusted-sites`.
        """)

    with st.container(border=True):
        st.markdown("### ⚙️ 4. Key Functional Features")
        f_col1, f_col2 = st.columns(2)
        with f_col1:
            st.markdown("""
            **Public / Vendor Experience:**
            - **Natural Language Category Matcher:** Semantic intent detection mapping products to official pre-approved categories.
            - **Interactive Functional Checklists:** Dynamic requirement questionnaires pulled directly from authoritative markdown sources.
            - **Prerequisite Validation Engine:** Instant checks for incorporation tenure, Current Ratio $\\ge 1$, net positive equity, and InvoiceNow registration.
            - **Interactive Remediation Copilot:** Floating assistant that accepts detected compliance gaps to suggest actionable remediation steps.
            """)
        with f_col2:
            st.markdown("""
            **Officer / Administrative Governance:**
            - **Automated Harvesting Daemon:** Daily GitHub Actions runner (`daily_refresh.yml`) synchronizing remote docs at 03:00 SGT.
            - **On-Demand Cache Invalidation:** Instant flush button executing `st.cache_data.clear()` for real-time policy synchrony.
            - **Intake Cycle Governance:** Operational controls governing active vendor application windows.
            - **Session Telemetry Registry:** Live runtime audit trail capturing submitted vendor assessments.
            """)

    render_footer_disclaimer()

# =========================================================
# PAGE 4: METHODOLOGY & SYSTEM ARCHITECTURE
# =========================================================

elif st.session_state.page == "Methodology":
    render_brand_header(
        "Methodology & System Architecture",
        subtitle="Data flowcharts, implementation details, cybersecurity guardrails, and decoupled architecture.",
        badge="System Architecture"
    )

    st.markdown("### 🔄 1. Process Flowcharts by Use Case")
    st.caption("Visual operational process flows implemented within the application:")

    tab_flow1, tab_flow2 = st.tabs([
        "Flowchart A: Automated Ingestion & Knowledge Refresh",
        "Flowchart B: Guided Vendor Self-Assessment & Grounded Copilot"
    ])

    # USE CASE 1 FLOWCHART
    with tab_flow1:
        with st.container(border=True):
            st.markdown("#### Use Case A: Headless Automated Knowledge Harvesting Daemon")
            st.markdown("""
            ```mermaid
            flowchart TD
                A[GitHub Actions Cron: 0 19 * * * / 3 AM SGT] --> B[Spin up Ubuntu 3.11 Headless Runner]
                B --> C[Execute imda_knowledge.py]
                C --> D[Crawl Official Endpoints from preapproval-guide.imda.gov.sg]
                D --> E[Parse & Validate Markdown Structure]
                E --> F{Content Changed?}
                F -- Yes --> G[Serialize to data/knowledge_index.json & Git Commit]
                F -- No --> H[Preserve Existing Version]
                G --> I[Streamlit App Ingests via In-Memory TTL Cache]
                H --> I
                J[Admin Hits 'Force Cache Flush'] -.->|On Demand| I
            ```
            """)
            st.caption("Figure 1.1: Automated CI/CD headless scraping daemon and synchronization pipeline.")

    # USE CASE 2 FLOWCHART
    with tab_flow2:
        with st.container(border=True):
            st.markdown("#### Use Case B: Vendor Self-Assessment & Grounded RAG Copilot")
            st.markdown("""
            ```mermaid
            flowchart TD
                U[Vendor Enters Solution Description] --> SEC[assessment_service: Adversarial Regex & XSS Sanitizer]
                SEC --> CHK{Injection Detected?}
                CHK -- Yes --> BLK[Return Security Warning & Halt Execution]
                CHK -- No --> AI1[Semantic Category Matcher - Gemini 2.5 Flash]
                AI1 --> S2[Step 2: Category Functional Checklist Extraction]
                S2 --> S3[Step 3: Corporate & Financial Prerequisite Validation]
                S3 --> S4[Step 4: Audit & Remediation Handover]
                S4 --> GAP{Compliance Gaps Found?}
                GAP -- Yes --> COP[Pass Gaps to Persistent AI Copilot via XML Boundaries]
                GAP -- No --> VMP[Direct Launch Link to Stage 2 & VMP Portal]
                COP --> RAG[Query Live Grounded Guide via google-genai]
                RAG --> ANS[Deliver Actionable Remediation Guidance]
            ```
            """)
            st.caption("Figure 1.2: End-to-end multi-stage assessment funnel and contextual Copilot interaction.")

    st.markdown("<div class='portal-spacer-md'></div>", unsafe_allow_html=True)

    with st.container(border=True):
        st.markdown("### 2. Multi-Turn RAG Pipeline & Prompt Engineering")
        st.markdown("""
        The conversational copilot uses **Google GenAI (`gemini-2.5-flash`)** orchestrated through a grounded Retrieval-Augmented Generation (RAG) architecture:
        - **Live Document Ingestion & Caching:** Pulls and caches markdown pages directly from the official portal (`https://preapproval-guide.imda.gov.sg/`) with TTL cache expiration to ensure compliance with the latest policy updates.
        - **XML Boundary Delimitation:** Untrusted vendor inputs and authoritative knowledge snippets are encapsulated within strict `<user_query>`, `<conversation_history>`, `<applicant_state>`, and `<context>` XML boundaries to prevent context bleeding.
        - **Conversational Memory:** Preserves multi-turn state across interactions, allowing vendors to ask follow-up questions regarding specific checklist items or financial ratios without losing state.
        - **Zero-Shot Semantic Matching:** Translates unstructured vendor solution descriptions into official IMDA categories using constrained JSON-like structural parsing.
        """)

    with st.container(border=True):
        st.markdown("### 3. Cybersecurity & Prompt Injection Defenses")
        st.markdown("""
        To safeguard public sector compliance integrity and prevent prompt tampering:
        - **Adversarial Regex Heuristics:** Evaluates incoming user inputs against multi-pattern jailbreak filters (e.g., `ignore previous instructions`, `system prompt`, `bypass guardrail`, `reveal API key`).
        - **XSS & Code Injection Sanitization:** Encodes angle brackets (`<`, `>`) and strips script tags (`<script>`, `javascript:`) before passing strings into the execution context.
        - **Prototype Passcode Gating:** Restricts prototype access via environment-managed passcodes verified against Streamlit Secrets.
        - **No Client-Side Credential Exposure:** All API keys (`GEMINI_API_KEY`) remain strictly server-side and are never serialized to the client browser.
        """)

    with st.container(border=True):
        st.markdown("### 4. Modular Engineering Blueprint (6 Decoupled Modules)")
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            with st.container(border=True):
                st.markdown("#### `app.py`")
                st.caption("Main Orchestration Engine")
                st.markdown("Controls authentication gating, session state initialization, routing across primary views (Home, Assessment, About, Methodology), Admin console logic, and the persistent floating Copilot modal.")
            
            with st.container(border=True):
                st.markdown("#### `assessment_module.py`")
                st.caption("Self-Assessment View Controller")
                st.markdown("Encapsulates the presentation layer for all 4 assessment steps (Discovery, Functional Checklist, Prerequisite Tabs, and Review & Submission Summary) with interactive deep-linking and unlisted category EOI routing.")

            with st.container(border=True):
                st.markdown("#### `assessment_schemas.py`")
                st.caption("Single Source of Truth Policy Schema")
                st.markdown("Centralizes baseline criteria (Singapore incorporation, 18-month operational history, positive net equity, Current Ratio $\\ge 1$, InvoiceNow status, and SME deployment benchmarks).")

        with col_m2:
            with st.container(border=True):
                st.markdown("#### `assessment_service.py`")
                st.caption("Scraping, Security & AI Matcher")
                st.markdown("Handles remote markdown scraping from `preapproval-guide.imda.gov.sg`, requirement regex extraction, adversarial input sanitization, and Gemini-powered category recommendations.")

            with st.container(border=True):
                st.markdown("#### `ui_components.py`")
                st.caption("Design System & Brand Styling")
                st.markdown("Implements the official SMEs Go Digital visual language: purple/magenta gradient lockups, Singapore Government `.gov.sg` masthead drawer, purple segmented stepper, card tokens, and expandable governance disclaimer.")

            with st.container(border=True):
                st.markdown("#### `imda_knowledge.py`")
                st.caption("Grounded Knowledge Engine")
                st.markdown("Manages portal constants, system prompt definitions, XML formatting for live RAG retrieval, and execution calls to the Gemini API client.")

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
