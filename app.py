"""
UI/UX Component & Style Library for IMDA Pre-Approval Assistant.
Matched to the SMEs Go Digital portal design guidelines.
"""

import streamlit as st

def inject_custom_css():
    """Injects SMEs Go Digital theme styling."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #212529;
        }

        /* Top Application Bar & Main Headers */
        .brand-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e3e8ee;
            margin-bottom: 20px;
        }
        .brand-title {
            font-size: 26px;
            font-weight: 700;
            color: #1b365d;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .brand-badge {
            background-color: #fce8e8;
            color: #d8232a;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid #f8b4b4;
        }

        /* SMEs Go Digital Hero Container */
        .sgds-hero {
            background: linear-gradient(135deg, #182f59 0%, #1b365d 60%, #224270 100%);
            color: #ffffff;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 24px;
            box-shadow: 0 4px 14px rgba(24, 47, 89, 0.15);
        }
        .sgds-hero h2 {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #ffffff !important;
        }
        .sgds-hero p {
            font-size: 14.5px;
            color: #e3e8ee;
            margin: 0;
            max-width: 90%;
            line-height: 1.5;
        }

        /* Feature Cards */
        .feature-card {
            background-color: #ffffff;
            border: 1px solid #e3e8ee;
            border-radius: 8px;
            padding: 22px;
            min-height: 170px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
            transition: all 0.2s ease-in-out;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .feature-card:hover {
            border-color: #1b365d;
            box-shadow: 0 6px 16px rgba(27, 54, 93, 0.08);
            transform: translateY(-2px);
        }
        .feature-icon {
            font-size: 24px;
            margin-bottom: 10px;
        }
        .feature-title {
            font-size: 17px;
            font-weight: 650;
            color: #1b365d;
            margin-bottom: 6px;
        }
        .feature-desc {
            font-size: 13px;
            color: #556575;
            line-height: 1.5;
            margin-bottom: 12px;
        }

        /* Readiness Audit KPI Tiles */
        .metric-tile {
            background: #f8fafc;
            border: 1px solid #e3e8ee;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }
        .metric-number {
            font-size: 28px;
            font-weight: 700;
            color: #1b365d;
        }
        .metric-label {
            font-size: 12px;
            font-weight: 600;
            color: #556575;
            text-transform: uppercase;
        }

        /* Streamlit Primary Button Override (SMEs Go Digital Red) */
        button[kind="primary"] {
            background-color: #d8232a !important;
            border-color: #d8232a !important;
            color: #ffffff !important;
            border-radius: 6px !important;
            font-weight: 600 !important;
        }
        button[kind="primary"]:hover {
            background-color: #b51c22 !important;
            border-color: #b51c22 !important;
        }

        /* Streamlit Secondary Button Override */
        button[kind="secondary"] {
            border-color: #ccd5df !important;
            color: #1b365d !important;
            border-radius: 6px !important;
            font-weight: 500 !important;
        }
        button[kind="secondary"]:hover {
            border-color: #1b365d !important;
            color: #182f59 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_brand_header(title: str, subtitle: str = None, badge: str = "Live Pilot"):
    """Renders a consistent top header matching the portal theme."""
    badge_html = f'<span class="brand-badge">{badge}</span>' if badge else ""
    st.markdown(
        f"""
        <div class="brand-header">
            <h1 class="brand-title">{title}</h1>
            {badge_html}
        </div>
        """,
        unsafe_allow_html=True
    )
    if subtitle:
        st.caption(subtitle)

def render_hero_banner(heading: str, description: str):
    """Renders the top banner container."""
    st.markdown(
        f"""
        <div class="sgds-hero">
            <h2>{heading}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_feature_card(icon: str, title: str, description: str):
    """Renders feature card containers."""
    st.markdown(
        f"""
        <div class="feature-card">
            <div>
                <div class="feature-icon">{icon}</div>
                <div class="feature-title">{title}</div>
                <div class="feature-desc">{description}</div>
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
                <div class="metric-number" style="color: {'#16a34a' if readiness_pct >= 80 else '#d97706'};">{readiness_pct}%</div>
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
                <div class="metric-number" style="color: #1b365d;">{in_progress}</div>
                <div class="metric-label">In-Progress Items</div>
            </div>
            """,
            unsafe_allow_html=True
        )
