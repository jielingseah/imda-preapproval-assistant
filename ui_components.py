"""
UI/UX Component & Style Library for IMDA Pre-Approval Assistant.
Faithfully styled according to the official SMEs Go Digital (smesgodigital.gov.sg) portal.
"""

import streamlit as st

def inject_custom_css():
    """Injects SMEs Go Digital official portal theme styling, including sidebar upgrades."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] {
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, sans-serif;
            color: #1a1a24;
        }

        /* Top Government Masthead */
        .sg-masthead {
            background-color: #f0f0f2;
            padding: 5px 16px;
            font-size: 11.5px;
            color: #4b4b5a;
            display: flex;
            align-items: center;
            gap: 8px;
            border-bottom: 1px solid #e2e2e8;
            margin: -6rem -5rem 1.5rem -5rem;
        }
        .sg-masthead-crest {
            color: #d8232a;
            font-weight: 700;
            font-size: 13px;
        }
        .sg-masthead a {
            color: #2b5cb8;
            text-decoration: underline;
            cursor: pointer;
        }

        /* SMEs Go Digital Brand Logo Header */
        .brand-logo-container {
            display: flex;
            align-items: baseline;
            gap: 14px;
            padding: 8px 0 16px 0;
            border-bottom: 1px solid #ebebf2;
            margin-bottom: 22px;
        }
        .logo-smes {
            font-size: 26px;
            font-weight: 800;
            color: #581845;
            letter-spacing: -0.5px;
            line-height: 1;
        }
        .logo-godigital {
            font-size: 26px;
            font-weight: 800;
            color: #d8232a;
            letter-spacing: -0.5px;
            line-height: 1;
        }
        .logo-subtitle {
            font-size: 13px;
            font-weight: 600;
            color: #6c6c7d;
            border-left: 2px solid #d0d0dc;
            padding-left: 12px;
            margin-left: 4px;
        }
        .brand-badge {
            background: linear-gradient(135deg, #581845 0%, #d8232a 100%);
            color: #ffffff;
            font-size: 10px;
            font-weight: 700;
            padding: 3px 9px;
            border-radius: 999px;
            text-transform: uppercase;
            letter-spacing: 0.6px;
            margin-left: auto;
        }

        /* SMEs Go Digital Signature Purple/Magenta Mesh Banner */
        .smes-banner {
            background: linear-gradient(130deg, #3d0c3f 0%, #5d1a58 35%, #7a1d5a 70%, #9a1f52 100%);
            color: #ffffff;
            padding: 36px 36px;
            border-radius: 18px;
            margin-bottom: 28px;
            box-shadow: 0 12px 28px -6px rgba(61, 12, 63, 0.28);
            position: relative;
            overflow: hidden;
        }
        .smes-banner::after {
            content: "";
            position: absolute;
            top: -50%;
            right: -10%;
            width: 320px;
            height: 320px;
            background: radial-gradient(circle, rgba(216, 35, 42, 0.25) 0%, rgba(255,255,255,0) 70%);
            pointer-events: none;
        }
        .smes-banner h2 {
            font-size: 26px;
            font-weight: 800;
            color: #ffffff !important;
            margin: 0 0 10px 0;
            letter-spacing: -0.5px;
        }
        .smes-banner p {
            font-size: 15px;
            color: #f3d7e8;
            margin: 0;
            max-width: 85%;
            line-height: 1.55;
            font-weight: 400;
        }

        /* Pill Search Box simulation on home banner */
        .smes-search-pill {
            margin-top: 20px;
            background: #ffffff;
            border-radius: 999px;
            padding: 6px 8px 6px 20px;
            display: inline-flex;
            align-items: center;
            gap: 12px;
            width: 90%;
            box-shadow: 0 4px 14px rgba(0,0,0,0.12);
        }
        .smes-search-btn {
            background-color: #5d1a58;
            color: #ffffff;
            padding: 7px 20px;
            border-radius: 999px;
            font-size: 13px;
            font-weight: 700;
        }

        /* Portal Cards */
        .portal-card {
            background-color: #ffffff;
            border: 1px solid #ebebf2;
            border-radius: 14px;
            padding: 24px;
            min-height: 195px;
            box-shadow: 0 4px 12px rgba(26, 26, 36, 0.04);
            transition: all 0.25s ease-in-out;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .portal-card:hover {
            border-color: #7a1d5a;
            box-shadow: 0 12px 24px rgba(93, 26, 88, 0.12);
            transform: translateY(-3px);
        }
        .portal-card-tag {
            font-size: 11px;
            font-weight: 700;
            color: #7a1d5a;
            background-color: #f7eaf3;
            padding: 3px 8px;
            border-radius: 6px;
            width: fit-content;
            margin-bottom: 12px;
            text-transform: uppercase;
        }
        .portal-card-title {
            font-size: 18px;
            font-weight: 700;
            color: #2b0b2e;
            margin-bottom: 8px;
        }
        .portal-card-desc {
            font-size: 13px;
            color: #636375;
            line-height: 1.5;
            margin-bottom: 12px;
        }

        /* Readiness Audit Metric Tiles */
        .metric-tile {
            background: #faf7f9;
            border: 1px solid #ebdbe5;
            border-radius: 12px;
            padding: 18px;
            text-align: center;
        }
        .metric-number {
            font-size: 30px;
            font-weight: 800;
            color: #5d1a58;
        }
        .metric-label {
            font-size: 12px;
            font-weight: 700;
            color: #6c6c7d;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Buttons matching the portal */
        button[kind="primary"] {
            background: linear-gradient(135deg, #581845 0%, #7a1d5a 100%) !important;
            border: none !important;
            color: #ffffff !important;
            border-radius: 999px !important;
            font-weight: 700 !important;
            padding: 8px 24px !important;
            box-shadow: 0 4px 12px rgba(88, 24, 69, 0.25) !important;
            transition: all 0.2s ease !important;
        }
        button[kind="primary"]:hover {
            background: linear-gradient(135deg, #7a1d5a 0%, #d8232a 100%) !important;
            box-shadow: 0 6px 16px rgba(216, 35, 42, 0.3) !important;
            transform: translateY(-1px);
        }

        button[kind="secondary"] {
            border: 1.5px solid #d0c0cc !important;
            color: #581845 !important;
            border-radius: 999px !important;
            font-weight: 600 !important;
            background-color: #ffffff !important;
        }
        button[kind="secondary"]:hover {
            border-color: #581845 !important;
            background-color: #faf2f7 !important;
            color: #3d0c3f !important;
        }

        /* =========================================================
           SIDEBAR STYLING UPGRADES (SMEs Go Digital Theme)
           ========================================================= */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #faf7f9 0%, #f4eff3 100%);
            border-right: 1px solid #ebdbe5;
            padding-top: 1rem;
        }
        
        /* Sidebar headers & captions */
        [data-testid="stSidebar"] h3 {
            color: #581845 !important;
            font-weight: 800 !important;
            letter-spacing: -0.3px;
        }
        [data-testid="stSidebar"] p, [data-testid="stSidebar"] span {
            color: #636375;
        }

        /* Sidebar Radio Navigation Options */
        [data-testid="stSidebar"] .stRadio label {
            background-color: #ffffff;
            border: 1px solid #ebdbe5;
            border-radius: 8px;
            padding: 8px 12px;
            margin-bottom: 6px;
            transition: all 0.2s ease;
            width: 100%;
            font-weight: 600;
            color: #4a154b !important;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            background-color: #f7eaf3;
            border-color: #7a1d5a;
        }

        /* Logout / Lock Button inside Sidebar */
        [data-testid="stSidebar"] button {
            border-radius: 999px !important;
            border: 1.5px solid #d8232a !important;
            color: #d8232a !important;
            font-weight: 700 !important;
            background-color: #ffffff !important;
            transition: all 0.2s ease !important;
        }
        [data-testid="stSidebar"] button:hover {
            background-color: #fce8e8 !important;
            color: #b51c22 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_brand_header(title: str, subtitle: str = None, badge: str = "Prototype"):
    """Renders the top Singapore Government Masthead & SMEs Go Digital logo header."""
    badge_html = f'<span class="brand-badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="sg-masthead">
            <span class="sg-masthead-crest">🇸🇬</span> A Singapore Government Agency Website &nbsp;<a href="#">How to identify</a>
        </div>
        <div class="brand-logo-container">
            <div>
                <span class="logo-smes">SMEs</span> <span class="logo-godigital">godigital ↗</span>
                <span class="logo-subtitle">Pre-Approval Assistant</span>
            </div>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True
    )
    if subtitle:
        st.markdown(f"<p style='color:#636375; font-size:14px; margin-top:-12px; margin-bottom:18px;'>{subtitle}</p>", unsafe_allow_html=True)

def render_hero_banner(heading: str, description: str):
    """Renders the official purple-magenta mesh banner seen on smesgodigital.gov.sg."""
    st.markdown(
        f"""
        <div class="smes-banner">
            <h2>{heading}</h2>
            <p>{description}</p>
            <div class="smes-search-pill">
                <span style="color:#7a1d5a; font-weight:700;">🔍</span>
                <span style="color:#777788; font-size:13.5px; flex-grow:1;">Search pre-approved categories, eligibility criteria, grants...</span>
                <span class="smes-search-btn">Search</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_feature_card(tag: str, title: str, description: str):
    """Renders sleek portal cards with rounded corners and hover glow."""
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
    """Renders the readiness indicator tiles using the portal palette."""
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
