"""
ui_components.py
Provides UI styling, Singapore Government masthead, navigation header,
and portal card wrappers for the IMDA Pre-Approval AI Copilot.
"""

import streamlit as st


def inject_portal_css():
    """Injects core SMEs Go Digital branding and layout overrides."""
    st.markdown(
        """
        <style>
        /* Import clean corporate font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        }

        /* Top padding normalization */
        .block-container {
            padding-top: 1rem !important;
            padding-bottom: 3rem !important;
        }

        /* Masthead styling */
        .gov-masthead {
            background-color: #f0f0f0;
            padding: 4px 16px;
            font-size: 0.75rem;
            color: #484848;
            display: flex;
            align-items: center;
            border-bottom: 1px solid #e0e0e0;
            margin-bottom: 1rem;
        }
        .gov-masthead-crest {
            font-size: 0.85rem;
            margin-right: 6px;
        }

        /* Navbar container */
        .portal-nav-container {
            padding: 0.5rem 0 1.25rem 0;
            border-bottom: 1px solid #eaeaea;
            margin-bottom: 1.5rem;
        }

        /* Clickable Brand Logo Button override */
        div[data-testid="stColumn"]:has(button[key="nav_brand_home"]) button,
        button[key="nav_brand_home"],
        button[data-testid="baseButton-secondary"][aria-label*="SMEsgo"] {
            background: transparent !important;
            border: none !important;
            color: #b81424 !important;
            font-size: 1.45rem !important;
            font-weight: 800 !important;
            letter-spacing: -0.6px !important;
            padding: 0 !important;
            margin: 0 !important;
            text-align: left !important;
            box-shadow: none !important;
            height: auto !important;
            line-height: 1.2 !important;
        }
        div[data-testid="stColumn"]:has(button[key="nav_brand_home"]) button:hover,
        button[key="nav_brand_home"]:hover {
            color: #e02438 !important;
            background: transparent !important;
        }

        /* Official Prototype badge */
        .badge-official-prototype {
            background-color: #8b0000;
            color: #ffffff;
            font-size: 0.72rem;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            display: inline-block;
        }

        /* Standard button ergonomics in navbar */
        div[data-testid="stHorizontalBlock"] button {
            border-radius: 6px;
            font-weight: 500;
        }

        /* Floating Copilot launcher pinned bottom-right */
        .floating-copilot-anchor {
            position: fixed;
            bottom: 24px;
            right: 24px;
            z-index: 999999;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_gov_masthead():
    """Renders the standard Singapore Government identification banner."""
    st.markdown(
        """
        <div class="gov-masthead">
            <span class="gov-masthead-crest">🇸🇬</span>
            <span>A Singapore Government Agency Website</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_top_navbar(current_page: str):
    """
    Renders top navigation bar without redundant Home tab.
    Clicking the brand mark returns to the Home view.
    """
    st.markdown('<div class="portal-nav-container">', unsafe_allow_html=True)
    col_brand, col_preapp, col_about, col_method, col_logout = st.columns(
        [3.0, 2.2, 1.3, 1.4, 1.0], gap="small"
    )

    with col_brand:
        # Clickable brand title as home trigger
        if st.button("SMEsgodigital ↗", key="nav_brand_home", help="Back to Home"):
            st.session_state["current_page"] = "Home"
            st.session_state["show_copilot_dialog"] = False
            st.rerun()

    with col_preapp:
        is_active = current_page == "Pre-Approval Assessment"
        if st.button(
            "Pre-Approval Assessment",
            key="nav_assessment",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state["current_page"] = "Pre-Approval Assessment"
            st.session_state["show_copilot_dialog"] = False
            st.rerun()

    with col_about:
        is_active = current_page == "About Us"
        if st.button(
            "About Us",
            key="nav_about",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state["current_page"] = "About Us"
            st.session_state["show_copilot_dialog"] = False
            st.rerun()

    with col_method:
        is_active = current_page == "Methodology"
        if st.button(
            "Methodology",
            key="nav_methodology",
            type="primary" if is_active else "secondary",
            use_container_width=True,
        ):
            st.session_state["current_page"] = "Methodology"
            st.session_state["show_copilot_dialog"] = False
            st.rerun()

    with col_logout:
        if st.button("Log out", key="nav_logout", use_container_width=True):
            st.session_state["authenticated"] = False
            st.session_state["current_page"] = "Home"
            st.session_state["show_copilot_dialog"] = False
            st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


def render_page_header(title: str, subtitle: str, show_prototype_badge: bool = True):
    """Renders a standard page title block with an optional prototype pill."""
    col_header, col_badge = st.columns([5, 1])
    with col_header:
        st.markdown(f"## {title}")
        if subtitle:
            st.caption(subtitle)
    with col_badge:
        if show_prototype_badge:
            st.markdown(
                '<div style="text-align: right; margin-top: 10px;">'
                '<span class="badge-official-prototype">OFFICIAL PROTOTYPE</span>'
                '</div>',
                unsafe_allow_html=True,
            )
