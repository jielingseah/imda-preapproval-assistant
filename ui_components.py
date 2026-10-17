"""
UI/UX Component & Style Library for IMDA Pre-Approval Assistant.
Emulates Singapore Government Design System (SGDS) patterns.
"""

import streamlit as st

def inject_custom_css():
    """Injects modern, corporate-grade styling."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #1e293b;
        }

        /* Top Application Bar & Main Headers */
        .brand-header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e2e8f0;
            margin-bottom: 20px;
        }
        .brand-title {
            font-size: 26px;
            font-weight: 700;
            color: #0f172a;
            margin: 0;
            letter-spacing: -0.5px;
        }
        .brand-badge {
            background-color: #e0f2fe;
            color: #0284c7;
            font-size: 11px;
            font-weight: 700;
            padding: 3px 8px;
            border-radius: 9999px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* Modern Hero Container */
        .sgds-hero {
            background: linear-gradient(135deg, #0f385a 0%, #1e40af 100%);
            color: #ffffff;
            padding: 30px;
            border-radius: 12px;
            margin-bottom: 24px;
            box-shadow: 0 10px 20px -5px rgba(15, 56, 90, 0.2);
        }
        .sgds-hero h2 {
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 8px;
            color: #ffffff !important;
        }
        .sgds-hero p {
            font-size: 15px;
            color: #e2e8f0;
            margin: 0;
            max-width: 90%;
            line-height: 1.5;
        }

        /* Interactive Dashboard Feature Cards */
        .feature-card {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            border-radius: 12px;
            padding: 24px;
            min-height: 180px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            transition: all 0.2s ease-in-out;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .feature-card:hover {
            border-color: #3b82f6;
            box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.1);
            transform: translateY(-2px);
        }
        .feature-icon {
            font-size: 24px;
            margin-bottom: 12px;
        }
        .feature-title {
            font-size: 18px;
            font-weight: 650;
            color: #0f172a;
            margin-bottom: 8px;
        }
        .feature-desc {
            font-size: 13px;
            color: #64748b;
            line-height: 1.5;
            margin-bottom: 12px;
        }

        /* Readiness Audit KPI Tiles */
        .metric-tile {
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 10px;
            padding: 16px;
            text-align: center;
        }
        .metric-number {
            font-size: 28px;
            font-weight: 700;
            color: #0f172a;
        }
        .metric-label {
            font-size: 12px;
            font-weight: 600;
            color: #64748b;
            text-transform: uppercase;
        }

        /* Chat Layout & Polish */
        .stChatMessage {
            border-radius: 10px !important;
            padding: 14px 18px !important;
            margin-bottom: 12px !important;
        }
        div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
            background-color: #f1f5f9;
        }
        div[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
            background-color: #ffffff;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def render_brand_header(title: str, subtitle: str = None, badge: str = "Live Pilot"):
    """Renders a consistent top header across pages."""
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
    """Renders an executive hero card."""
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
    """Renders visual interactive card containers."""
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
    """Renders visual readiness score indicators."""
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
                <div class="metric-number" style="color: {'#dc2626' if gaps > 0 else '#16a34a'};">{gaps}</div>
                <div class="metric-label">Prerequisite Gaps</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        st.markdown(
            f"""
            <div class="metric-tile">
                <div class="metric-number" style="color: #0284c7;">{in_progress}</div>
                <div class="metric-label">In-Progress Items</div>
            </div>
            """,
            unsafe_allow_html=True
        )
