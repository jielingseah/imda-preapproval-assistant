import streamlit as st
from datetime import datetime
import pandas as pd

# 1. MUST BE THE VERY FIRST STREAMLIT CALL
st.set_page_config(
    page_title="IMDA Pre-Approval Assistant",
    page_icon="🇸🇬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2. Imports after set_page_config
from ui_components import render_portal_header, load_custom_css
from assessment_module import render_pre_approval_assessment
from imda_knowledge import MODEL_NAME, crawl_imda_guide

# 3. Load CSS styles
load_custom_css()

# ---------------------------------------------------------
# Session State Defaults
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_role" not in st.session_state:
    st.session_state.user_role = "User"
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
if "admin_view_mode" not in st.session_state:
    st.session_state.admin_view_mode = "🔍 Vendor Assessment View"

# ---------------------------------------------------------
# View 1: Gated Authentication Screen
# ---------------------------------------------------------
if not st.session_state.authenticated:
    render_header()
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
                    # Safely fetch secret with fallback
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

    render_footer()
    st.stop()  # Stop execution here until authenticated

# ---------------------------------------------------------
# View 2: Authenticated Main Portal (No Sidebar)
# ---------------------------------------------------------
render_header()

# Top Utility Bar (Role indicator, Admin switcher, Logout)
with st.container():
    if st.session_state.user_role == "Admin":
        col_info, col_toggle, col_logout = st.columns([2.8, 4.2, 1.2])
        with col_info:
            st.markdown(
                "<span style='background:#ede9fe; color:#5b21b6; padding:4px 10px; border-radius:12px; font-size:12.5px; font-weight:600;'>"
                "🛡️ Mode: IMDA Reviewing Officer (Admin)"
                "</span>",
                unsafe_allow_html=True
            )
        with col_toggle:
            st.session_state.admin_view_mode = st.radio(
                "Admin Navigation",
                ["🔍 Vendor Assessment View", "⚙️ Officer Operations Console"],
                index=0 if st.session_state.admin_view_mode == "🔍 Vendor Assessment View" else 1,
                horizontal=True,
                label_visibility="collapsed"
            )
        with col_logout:
            if st.button("Log Out ↪", key="btn_top_logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_role = "User"
                st.rerun()
    else:
        col_info, _, col_logout = st.columns([4, 4, 1.2])
        with col_info:
            st.markdown(
                "<span style='background:#f1f5f9; color:#334155; padding:4px 10px; border-radius:12px; font-size:12.5px; font-weight:600;'>"
                "👤 Mode: ICM Vendor Applicant"
                "</span>",
                unsafe_allow_html=True
            )
        with col_logout:
            if st.button("Log Out ↪", key="btn_top_logout", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user_role = "User"
                st.rerun()

st.markdown("<hr style='margin: 10px 0 18px 0; border: none; border-top: 1px solid #e2e8f0;'>", unsafe_allow_html=True)

# Main Content Routing
if st.session_state.user_role == "Admin" and st.session_state.admin_view_mode == "⚙️ Officer Operations Console":
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
                    with st.spinner("Scraping and re-indexing official IMDA guide markdown pages..."):
                        st.cache_data.clear()
                        crawl_imda_guide()
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
            st.markdown(f"- **Primary LLM:** `{MODEL_NAME}` (Google GenAI)")
            st.markdown("- **Prompt Scaffolding:** XML-delimited (`<official_knowledge_base>`, `<vendor_context>`)")
            st.markdown("- **Input Defense:** Regex-based heuristic pattern defense (Jailbreak / Injection interception)")
            st.markdown(f"- **Officer Notification Route:** `{st.secrets.get('OFFICER_REVIEW_EMAIL', 'seah_jie_ling@imda.gov.sg')}`")
else:
    render_pre_approval_assessment()

render_footer()
