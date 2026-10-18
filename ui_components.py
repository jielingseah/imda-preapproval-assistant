"""
UI/UX Component & Style Library for IMDA Pre-Approval Assistant.
Faithfully styled according to the official SMEs Go Digital (smesgodigital.gov.sg) portal header.
"""

import streamlit as st

def inject_custom_css():
    """Injects SMEs Go Digital official portal header styling and hides default elements."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
            color: #1a1a24;
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

        /* SMEs Go Digital Brand Logo Header Bar */
        .portal-header-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 8px 0 14px 0;
            border-bottom: 1px solid #eaeaef;
            margin-bottom: 24px;
            background-color: #ffffff;
        }
        .logo-container {
            display: flex;
            align-items: baseline;
            gap: 12px;
        }
        .logo-smes {
            font-size: 24px;
            font-weight: 800;
            color: #581845;
            letter-spacing: -0.5px;
            line-height: 1;
        }
        .logo-godigital {
            font-size: 24px;
            font-weight: 800;
            color: #d8232a;
            letter-spacing: -0.5px;
            line-height: 1;
        }
        .logo-subtitle {
            font-size: 12px;
            font-weight: 600;
            color: #777788;
            border-left: 2px solid #d0d0dc;
            padding-left: 10px;
        }

        /* Sleek Top Nav Links */
        .nav-link-row {
            display: flex;
            align-items: center;
            gap: 24px;
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

        /* Readiness Audit Metric Tiles */
        .metric-tile {
            background: #faf7f9;
            border: 1px solid #ebdbe5;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        }
        .metric-number {
            font-size: 28px;
            font-weight: 800;
            color: #5d1a58;
        }
        .metric-label {
            font-size: 11.5px;
            font-weight: 700;
            color: #6c6c7d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Footer Prototype Notice Styling */
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
    """Renders the top navigation header bar matching smesgodigital.gov.sg cleanly without ugly buttons."""
    pages = [
        "Home",
        "Self-Assessment",
        "AI Category Finder",
        "Category Requirements",
        "AI Assistant (RAG Chatbot)",
        "About Us",
        "Methodology"
    ]

    current_page = st.session_state.get("page", "Home")

    # Top Masthead
    st.markdown(
        """
        <div class="sg-masthead">
            <span class="sg-masthead-crest">🇸🇬</span> A Singapore Government Agency Website &nbsp;<a href="#">How to identify ▾</a>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Header Bar layout
    col_logo, col_nav, col_actions = st.columns([2.2, 5.8, 2])

    with col_logo:
        st.markdown(
            """
            <div class="logo-container" style="padding-top: 4px;">
                <span class="logo-smes">SMEs</span><span class="logo-godigital">godigital ↗</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col_nav:
        # Render pages as clean inline link buttons
        nav_cols = st.columns(len(pages))
        for idx, page_name in enumerate(pages):
            with nav_cols[idx]:
                is_active = (current_page == page_name)
                # Style active page with bolder color / underline look via button styling
                btn_type = "primary" if is_active else "secondary"
                if st.button(page_name, key=f"sleek_nav_{idx}", type=btn_type, use_container_width=True):
                    st.session_state.page = page_name
                    st.rerun()

    with col_actions:
        col_srch, col_log = st.columns([1, 1])
        with col_srch:
            if st.button("🔍 Search", key="header_search_btn", use_container_width=True):
                st.session_state.page = "AI Category Finder"
                st.rerun()
        with col_log:
            if st.button("🔒 Logout", key="header_logout_btn", type="primary", use_container_width=True):
                st.session_state.authenticated = False
                st.rerun()

    st.markdown("<div style='border-bottom: 1px solid #eaeaef; margin-top: 8px; margin-bottom: 20px;'></div>", unsafe_allow_html=True)

def render_brand_header(title: str, subtitle: str = None, badge: str = "Prototype"):
    """Renders the sleek top navigation header bar and page title."""
    render_top_navigation()
    
    badge_html = f'<span style="background: linear-gradient(135deg, #581845 0%, #d8232a 100%); color: #fff; font-size: 10px; font-weight: 700; padding: 3px 9px; border-radius: 999px; text-transform: uppercase; float: right;">{badge}</span>'
    st.markdown(f"<div>{badge_html}<h1 style='font-size: 24px; font-weight: 800; color: #2b0b2e; margin: 0;'>{title}</h1></div>", unsafe_allow_html=True)
    
    if subtitle:
        st.markdown(f"<p style='color:#636375; font-size:13.5px; margin-top:4px; margin-bottom:18px;'>{subtitle}</p>", unsafe_allow_html=True)

def render_hero_banner(heading: str, description: str):
    """Renders the official purple-magenta mesh banner."""
    st.markdown(
        f"""
        <div style="background: linear-gradient(130deg, #3d0c3f 0%, #5d1a58 35%, #7a1d5a 70%, #9a1f52 100%); color: #ffffff; padding: 32px 32px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 24px -6px rgba(61, 12, 63, 0.25);">
            <h2 style="font-size: 24px; font-weight: 800; color: #ffffff !important; margin: 0 0 8px 0;">{heading}</h2>
            <p style="font-size: 14.5px; color: #f3d7e8; margin: 0; max-width: 85%; line-height: 1.5;">{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_feature_card(tag: str, title: str, description: str):
    """Renders sleek portal cards."""
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

def render_kpi_dashboard(readiness_pct: int, gaps: int, in_progress: int):
    """Renders readiness indicator tiles."""
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-number" style="color: {'#16a34a' if readiness_pct >= 80 else '#c2410c'};">{readiness_pct}%</div>
                <div class="metric-label">Readiness Score</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col2:
        st.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-number" style="color: {'#d8232a' if gaps > 0 else '#16a34a'};">{gaps}</div>
                <div class="metric-label">Prerequisite Gaps</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-number" style="color: #5d1a58;">{in_progress}</div>
                <div class="metric-label">In-Progress Items</div>
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
