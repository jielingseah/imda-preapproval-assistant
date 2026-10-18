"""
UI/UX Component & Style Library for IMDA Pre-Approval Assistant.
Faithfully styled according to the official SMEs Go Digital (smesgodigital.gov.sg) portal.
"""

import streamlit as st

def inject_custom_css():
    """Injects universal Plus Jakarta Sans font, floating copilot widget styles, and SMEs Go Digital branding."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

        /* UNIVERSAL FONT SYNC */
        html, body, [class*="css"], [class*="st-"], 
        h1, h2, h3, h4, h5, h6, p, div, span, label, input, textarea, button {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            letter-spacing: -0.01em;
        }

        /* Hide Streamlit default sidebar and header decorations */
        [data-testid="stSidebar"] {
            display: none !important;
        }
        header {visibility: hidden;}

        /* Top Government Masthead */
        .sg-masthead {
            background-color: #f8f8f9;
            padding: 4px 16px;
            font-size: 11px;
            color: #555566;
            display: flex;
            align-items: center;
            gap: 6px;
            border-bottom: 1px solid #eaeaf0;
            margin: -6rem -5rem 0.8rem -5rem;
        }
        .sg-masthead-crest {
            color: #d8232a;
            font-weight: 700;
        }
        .sg-masthead a {
            color: #2b5cb8;
            text-decoration: none;
        }

        /* Sleek Lilac Search Pill */
        div[data-testid="column"]:has(button[key="header_search_btn"]) button,
        button[key="header_search_btn"] {
            background-color: #f1e6f5 !important;
            color: #581845 !important;
            border: none !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            padding: 0 16px !important;
        }
        div[data-testid="column"]:has(button[key="header_search_btn"]) button:hover,
        button[key="header_search_btn"]:hover {
            background-color: #e5d4ec !important;
            color: #420f34 !important;
        }

        /* Sleek Deep Purple Logout Pill */
        div[data-testid="column"]:has(button[key="header_logout_btn"]) button,
        button[key="header_logout_btn"] {
            background-color: #6a1a72 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            font-size: 13px !important;
            padding: 0 18px !important;
        }
        div[data-testid="column"]:has(button[key="header_logout_btn"]) button:hover,
        button[key="header_logout_btn"]:hover {
            background-color: #521358 !important;
            color: #ffffff !important;
        }

        /* Floating Chatbot Launch Trigger Button in Bottom-Right Corner */
        div.st-key-floating_chat_trigger button {
            position: fixed !important;
            bottom: 26px !important;
            right: 28px !important;
            z-index: 999999 !important;
            border-radius: 50px !important;
            padding: 12px 22px !important;
            background: linear-gradient(135deg, #581845 0%, #7a1d5a 50%, #d8232a 100%) !important;
            color: #ffffff !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            border: 2px solid #ffffff !important;
            box-shadow: 0 8px 24px rgba(88, 24, 69, 0.35) !important;
            transition: all 0.25s ease-in-out !important;
        }
        div.st-key-floating_chat_trigger button:hover {
            transform: scale(1.05) translateY(-2px) !important;
            box-shadow: 0 12px 30px rgba(88, 24, 69, 0.45) !important;
        }

        /* Portal Cards */
        .portal-card {
            background-color: #ffffff;
            border: 1px solid #ebebf2;
            border-radius: 12px;
            padding: 22px;
            min-height: 185px;
            box-shadow: 0 4px 12px rgba(26, 26, 36, 0.04);
            transition: all 0.25s ease-in-out;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .portal-card:hover {
            border-color: #7a1d5a;
            box-shadow: 0 10px 20px rgba(93, 26, 88, 0.1);
            transform: translateY(-2px);
        }
        .portal-card-tag {
            font-size: 11px;
            font-weight: 700;
            color: #7a1d5a;
            background-color: #f7eaf3;
            padding: 3px 8px;
            border-radius: 6px;
            width: fit-content;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .portal-card-title {
            font-size: 17px;
            font-weight: 700;
            color: #2b0b2e;
            margin-bottom: 6px;
        }
        .portal-card-desc {
            font-size: 12.5px;
            color: #636375;
            line-height: 1.45;
            margin-bottom: 10px;
        }

        /* Footer Prototype Notice */
        .prototype-footer {
            margin-top: 50px;
            padding: 20px;
            background-color: #f8f8fa;
            border-top: 1px solid #e2e2e8;
            border-radius: 10px;
            text-align: center;
            color: #6c6c7d;
            font-size: 12px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_top_navigation():
    """Renders the streamlined 4-item top navigation header bar."""
    pages = [
        "Home",
        "Pre-Approval Assessment",
        "About Us",
        "Methodology"
    ]

    current_page = st.session_state.get("page", "Home")

    # Government Masthead
    st.markdown(
        """
        <div class="sg-masthead">
            <span class="sg-masthead-crest">🇸🇬</span> A Singapore Government Agency Website &nbsp;<a href="#">How to identify ▾</a>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Clean layout: Logo + 4 Nav items + Search Pill + Logout Pill
    cols = st.columns([2.5, 1.2, 2.3, 1.2, 1.3, 1.1, 1.0])

    with cols[0]:
        st.markdown(
            """
            <div style="padding-top: 4px;">
                <span style="font-size: 22px; font-weight: 800; color: #581845; letter-spacing: -0.5px;">SMEs</span><span style="font-size: 22px; font-weight: 800; color: #d8232a; letter-spacing: -0.5px;">godigital ↗</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    for idx, page_name in enumerate(pages):
        with cols[idx + 1]:
            is_active = (current_page == page_name)
            btn_type = "primary" if is_active else "secondary"
            if st.button(page_name, key=f"nav_link_{idx}", type=btn_type, use_container_width=True):
                st.session_state.page = page_name
                st.rerun()

    with cols[5]:
        if st.button("Search 🔍", key="header_search_btn", use_container_width=True):
            st.session_state.page = "Pre-Approval Assessment"
            st.session_state.assessment_step = 1  # jump straight to discovery
            st.rerun()

    with cols[6]:
        if st.button("Log out", key="header_logout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    st.markdown("<div style='border-bottom: 1px solid #eaeaef; margin-top: 8px; margin-bottom: 22px;'></div>", unsafe_allow_html=True)

def render_brand_header(title: str, subtitle: str = None, badge: str = "Official Prototype"):
    """Renders the top navigation header and section title."""
    render_top_navigation()
    
    badge_html = f'<span style="background: linear-gradient(135deg, #581845 0%, #d8232a 100%); color: #fff; font-size: 10px; font-weight: 700; padding: 3px 9px; border-radius: 999px; text-transform: uppercase; float: right;">{badge}</span>'
    st.markdown(f"<div>{badge_html}<h1 style='font-size: 24px; font-weight: 800; color: #2b0b2e; margin: 0;'>{title}</h1></div>", unsafe_allow_html=True)
    
    if subtitle:
        st.markdown(f"<p style='color:#636375; font-size:13.5px; margin-top:4px; margin-bottom:18px;'>{subtitle}</p>", unsafe_allow_html=True)

def render_hero_banner(heading: str, description: str):
    """Renders the purple-magenta mesh banner."""
    st.markdown(
        f"""
        <div style="background: linear-gradient(130deg, #3d0c3f 0%, #5d1a58 35%, #7a1d5a 70%, #9a1f52 100%); color: #ffffff; padding: 30px 32px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 24px -6px rgba(61, 12, 63, 0.25);">
            <h2 style="font-size: 24px; font-weight: 800; color: #ffffff !important; margin: 0 0 8px 0;">{heading}</h2>
            <p style="font-size: 14.5px; color: #f3d7e8; margin: 0; max-width: 85%; line-height: 1.5;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_feature_card(tag: str, title: str, description: str):
    """Renders portal cards."""
    st.markdown(
        f"""
        <div class="portal-card">
            <div>
                <div class="portal-card-tag">{tag}</div>
                <div class="portal-card-title">{title}</div>
                <div class="portal-card-desc">{description}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_footer_disclaimer():
    """Renders the prototype disclaimer at the bottom of each page."""
    st.markdown(
        """
        <div class="prototype-footer">
            <strong>⚠️ IMPORTANT NOTICE — Prototype:</strong> This web application is developed for demonstration purposes only under the IMDA SMEs Go Digital POC. 
            The information provided here is NOT intended for actual business or regulatory decisions.
        </div>
        """,
        unsafe_allow_html=True
    )
