"""
UI/UX Component & Style Library for IMDA Pre-Approval Assistant.
Faithfully styled according to the official SMEs Go Digital (smesgodigital.gov.sg) portal.
"""

import streamlit as st

def inject_custom_css():
    """Injects universal font, trims top whitespace, and fixes floating elements."""
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&display=swap');

        /* Clean White Base Portal Background */
        html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background-color: #ffffff !important;
            color: #2b0b2e;
        }

        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 3rem !important;
            max-width: 95% !important;
            background-color: #ffffff !important;
        }

        /* Universal Typography Sync */
        html, body, [class*="css"], [class*="st-"], [data-testid="stMarkdownContainer"],
        h1, h2, h3, h4, h5, h6, p, div, span, label, input, textarea, button, a {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            letter-spacing: -0.015em !important;
        }

        /* Proportional Heading Scale */
        [data-testid="stMarkdownContainer"] h1, h1 {
            font-size: 21px !important;
            font-weight: 800 !important;
            color: #2b0b2e !important;
            line-height: 1.3 !important;
            margin-top: 0.2rem !important;
            margin-bottom: 0.4rem !important;
        }

        [data-testid="stMarkdownContainer"] h2, h2 {
            font-size: 18px !important;
            font-weight: 800 !important;
            color: #2b0b2e !important;
            line-height: 1.35 !important;
            margin-top: 0.8rem !important;
            margin-bottom: 0.4rem !important;
        }

        [data-testid="stMarkdownContainer"] h3, h3 {
            font-size: 16px !important;
            font-weight: 700 !important;
            color: #2b0b2e !important;
            line-height: 1.4 !important;
            margin-top: 0.8rem !important;
            margin-bottom: 0.4rem !important;
        }

        [data-testid="stMarkdownContainer"] h4, h4 {
            font-size: 14.5px !important;
            font-weight: 700 !important;
            color: #2b0b2e !important;
            line-height: 1.4 !important;
        }

        [data-testid="stMarkdownContainer"] p {
            font-size: 13px !important;
            color: #555566 !important;
            line-height: 1.5 !important;
        }

        html {
            scroll-behavior: smooth !important;
        }

        [data-testid="stSidebar"] {
            display: none !important;
        }
        header {visibility: hidden;}

        /* Top Government Masthead & Interactive Expandable Drawer */
        .sg-masthead {
            background-color: #f0f0f0;
            border-bottom: 1px solid #e5e5e5;
            margin: 0 -5rem 12px -5rem;
            font-size: 11.5px;
            color: #484848;
        }
        .sg-masthead-summary {
            padding: 5px 24px;
            display: flex;
            align-items: center;
            gap: 6px;
            cursor: pointer;
            user-select: none;
            list-style: none;
            outline: none;
        }
        .sg-masthead-summary::-webkit-details-marker {
            display: none;
        }
        .sg-masthead-crest {
            color: #d8232a;
            font-weight: 700;
            font-size: 13px;
        }
        .sg-masthead-trigger {
            color: #2b5cb8;
            text-decoration: underline;
            margin-left: 3px;
            cursor: pointer;
        }
        .sg-masthead-trigger:hover {
            color: #1a3c7a;
        }
        .sg-masthead-drawer {
            background-color: #f0f0f0;
            border-top: 1px solid #e0e0e0;
            padding: 16px 24px 20px 24px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 28px;
        }
        .sg-masthead-col {
            display: flex;
            align-items: flex-start;
            gap: 12px;
        }
        .sg-masthead-icon {
            font-size: 17px;
            line-height: 1.2;
            color: #333333;
        }
        .sg-masthead-text-title {
            font-size: 12.5px;
            font-weight: 700;
            color: #222222;
            margin-bottom: 3px;
        }
        .sg-masthead-text-desc {
            font-size: 11.5px;
            color: #555566;
            line-height: 1.45;
            margin: 0;
        }
        .sg-masthead-text-desc a {
            color: #2b5cb8;
            text-decoration: underline;
        }

        /* Invisible Logo Overlay */
        div.st-key-nav_logo_overlay_btn {
            margin-top: -40px !important;
            height: 38px !important;
            width: 195px !important;
        }
        div.st-key-nav_logo_overlay_btn button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            height: 38px !important;
            width: 195px !important;
            cursor: pointer !important;
            color: transparent !important;
            padding: 0 !important;
            margin: 0 !important;
        }
        div.st-key-nav_logo_overlay_btn button:hover,
        div.st-key-nav_logo_overlay_btn button:focus,
        div.st-key-nav_logo_overlay_btn button:active {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            color: transparent !important;
        }

        /* Logout Pill */
        button[key="header_logout_btn"] {
            background-color: #6a1a72 !important;
            color: #ffffff !important;
            border: none !important;
            border-radius: 50px !important;
            font-weight: 700 !important;
            font-size: 13px !important;
        }
        button[key="header_logout_btn"]:hover {
            background-color: #521358 !important;
            color: #ffffff !important;
        }

        /* Floating Back-to-Top Button */
        .floating-action-bar {
            position: fixed !important;
            bottom: 24px !important;
            right: 180px !important;
            z-index: 999998 !important;
        }
        .floating-top-link {
            border-radius: 50px !important;
            padding: 9px 18px !important;
            background-color: #ffffff !important;
            color: #581845 !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            border: 1.5px solid #d0c4d8 !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.08) !important;
            text-decoration: none !important;
            display: inline-block !important;
        }
        .floating-top-link:hover {
            background-color: #f7eaf3 !important;
            border-color: #7a1d5a !important;
            color: #7a1d5a !important;
        }

        /* Floating Copilot Button */
        div.st-key-floating_chat_button {
            position: fixed !important;
            bottom: 24px !important;
            right: 28px !important;
            z-index: 999999 !important;
        }
        div.st-key-floating_chat_button button {
            border-radius: 50px !important;
            padding: 10px 22px !important;
            background: linear-gradient(135deg, #581845 0%, #7a1d5a 50%, #d8232a 100%) !important;
            color: #ffffff !important;
            font-size: 13.5px !important;
            font-weight: 700 !important;
            border: 2px solid #ffffff !important;
            box-shadow: 0 8px 24px rgba(88, 24, 69, 0.35) !important;
        }
        div.st-key-floating_chat_button button:hover {
            transform: scale(1.04) translateY(-2px) !important;
            box-shadow: 0 12px 30px rgba(88, 24, 69, 0.45) !important;
        }

        /* Portal Badges and Cards */
        .portal-card-tag, .step-badge {
            font-size: 12.5px !important;
            font-weight: 800 !important;
            color: #7a1d5a !important;
            background-color: #f7eaf3 !important;
            border: 1px solid #ebd4e4 !important;
            padding: 4px 12px !important;
            border-radius: 8px !important;
            width: fit-content !important;
            margin-bottom: 10px !important;
            text-transform: uppercase !important;
            letter-spacing: 0.2px !important;
            display: inline-flex !important;
            align-items: center !important;
            gap: 6px !important;
        }

        .portal-card {
            background-color: #ffffff;
            border: 1px solid #ebebf2;
            border-radius: 12px;
            padding: 22px;
            min-height: 180px;
            box-shadow: 0 4px 12px rgba(26, 26, 36, 0.04);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .portal-card:hover {
            border-color: #7a1d5a;
            box-shadow: 0 10px 20px rgba(93, 26, 88, 0.08);
        }
        .portal-card-title {
            font-size: 16.5px !important;
            font-weight: 800 !important;
            color: #2b0b2e !important;
            margin-bottom: 8px !important;
            display: flex !important;
            align-items: center !important;
            gap: 8px !important;
        }
        .portal-card-desc {
            font-size: 13px;
            color: #636375;
            line-height: 1.5;
            margin-bottom: 10px;
        }

        /* Isolated Purple Stepper Box */
        div.st-key-stepper_isolated_container {
            background: linear-gradient(130deg, #3d0c3f 0%, #5d1a58 35%, #7a1d5a 70%, #9a1f52 100%) !important;
            border-radius: 16px !important;
            padding: 20px 24px 18px 24px !important;
            margin-bottom: 24px !important;
            box-shadow: 0 10px 24px -6px rgba(61, 12, 63, 0.25) !important;
        }

        div.st-key-stepper_isolated_container div[class*="st-key-stepper_click_"] button {
            box-shadow: none !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            text-align: center !important;
            padding: 8px 10px !important;
            border-radius: 8px !important;
            font-size: 12.5px !important;
            width: 100% !important;
        }
        div.st-key-stepper_isolated_container div[class*="st-key-stepper_click_"] button:hover {
            transform: translateY(-1px) !important;
        }

        /* Global Purple Action Buttons */
        button[kind="primary"],
        button[data-testid="baseButton-primary"] {
            background: linear-gradient(130deg, #581845 0%, #7a1d5a 50%, #9a1f52 100%) !important;
            color: #ffffff !important;
            border: 1px solid #7a1d5a !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 13.5px !important;
            box-shadow: 0 4px 12px rgba(88, 24, 69, 0.25) !important;
            transition: all 0.2s ease !important;
        }
        button[kind="primary"]:hover,
        button[data-testid="baseButton-primary"]:hover {
            background: linear-gradient(130deg, #481237 0%, #68174c 50%, #871946 100%) !important;
            color: #ffffff !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px rgba(88, 24, 69, 0.35) !important;
        }
        button[kind="primary"] p,
        button[kind="primary"] span,
        button[data-testid="baseButton-primary"] p,
        button[data-testid="baseButton-primary"] span {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
        }

        button[kind="secondary"],
        button[data-testid="baseButton-secondary"] {
            background-color: #ffffff !important;
            color: #581845 !important;
            border: 1.5px solid #d0c4d8 !important;
            border-radius: 8px !important;
            font-weight: 700 !important;
            font-size: 13.5px !important;
            transition: all 0.2s ease !important;
        }
        button[kind="secondary"]:hover,
        button[data-testid="baseButton-secondary"]:hover {
            background-color: #f7eaf3 !
