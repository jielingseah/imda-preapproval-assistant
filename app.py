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
        badge
