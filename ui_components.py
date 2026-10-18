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

        /* Combined Logo & Title Overlay Button */
        div.st-key-nav_logo_overlay_btn {
            margin-top: -46px !important;
            height: 44px !important;
            width: 100% !important;
            max-width: 330px !important;
        }
        div.st-key-nav_logo_overlay_btn button {
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
            height: 44px !important;
            width: 100% !important;
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

        /* Fixed Ask Copilot Button in bottom right */
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
        div.st-key-floating_chat_button button p,
        div.st-key-floating_chat_button button span {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            background: transparent !important;
            background-color: transparent !important;
            font-weight: 700 !important;
            opacity: 1 !important;
        }
        div.st-key-floating_chat_button button:hover {
            transform: scale(1.04) translateY(-2px) !important;
            box-shadow: 0 12px 30px rgba(88, 24, 69, 0.45) !important;
        }
        div.st-key-floating_chat_button button:hover p,
        div.st-key-floating_chat_button button:hover span {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
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

        /* =========================================================
           GLOBAL PURPLE ACTION & FORM SUBMIT BUTTONS
           ========================================================= */
        button[kind="primary"],
        button[data-testid="baseButton-primary"],
        div[data-testid="stFormSubmitButton"] button,
        div[data-testid="stFormSubmitButton"] button[kind="primary"],
        div[data-testid="stFormSubmitButton"] button[data-testid="baseButton-primary"] {
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
        button[data-testid="baseButton-primary"]:hover,
        div[data-testid="stFormSubmitButton"] button:hover {
            background: linear-gradient(130deg, #481237 0%, #68174c 50%, #871946 100%) !important;
            color: #ffffff !important;
            border-color: #581845 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 6px 16px rgba(88, 24, 69, 0.35) !important;
        }

        button[kind="primary"] p,
        button[kind="primary"] span,
        button[data-testid="baseButton-primary"] p,
        button[data-testid="baseButton-primary"] span,
        div[data-testid="stFormSubmitButton"] button p,
        div[data-testid="stFormSubmitButton"] button span {
            color: #ffffff !important;
            -webkit-text-fill-color: #ffffff !important;
            background: transparent !important;
            background-color: transparent !important;
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
            background-color: #f7eaf3 !important;
            border-color: #7a1d5a !important;
            color: #7a1d5a !important;
        }

        button[kind="secondary"] p,
        button[kind="secondary"] span,
        button[data-testid="baseButton-secondary"] p,
        button[data-testid="baseButton-secondary"] span {
            color: #581845 !important;
            background: transparent !important;
            background-color: transparent !important;
        }

        /* Purple Sub-Tab Segmented Strip */
        div.st-key-prereq_subtab_bar {
            background: #f7eaf3 !important;
            padding: 5px !important;
            border-radius: 12px !important;
            border: 1px solid #ebd4e4 !important;
            margin-bottom: 20px !important;
        }
        div.st-key-prereq_subtab_bar div[class*="st-key-subtab_btn_"] button {
            border: none !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            font-size: 13px !important;
            font-weight: 700 !important;
            transition: all 0.2s ease !important;
        }

        .prototype-footer {
            margin-top: 40px;
            padding: 18px;
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
    """
    Renders top navigation with Singapore Government masthead and combined
    SMEs Go Digital + IMDA Pre-Approval Assistant logo linking directly to Home.
    """
    pages = [
        "Pre-Approval Assessment",
        "About Us",
        "Methodology"
    ]

    current_page = st.session_state.get("page", "Home")

    # Singapore Government Expandable Masthead
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
                            Government agencies communicate via .gov.sg websites (e.g. go.gov.sg/open). 
                            <a href="https://www.gov.sg/trusted-sites#govsites" target="_blank" rel="noopener noreferrer">Trusted websites ↗</a>
                        </p>
                    </div>
                </div>
                <div class="sg-masthead-col">
                    <span class="sg-masthead-icon">🔒</span>
                    <div>
                        <div class="sg-masthead-text-title">Secure websites use HTTPS</div>
                        <p class="sg-masthead-text-desc">
                            Look for a <strong>lock (🔒)</strong> or https:// as an added precaution. Share sensitive information only on official, secure websites.
                        </p>
                    </div>
                </div>
            </div>
        </details>
        """,
        unsafe_allow_html=True
    )

    # Navigation Layout: Expanded brand column + page links + logout
    cols = st.columns([4.2, 2.3, 1.2, 1.3, 1.0])

    with cols[0]:
        # Visual combined logo lockup
        st.markdown(
            """
            <div style="height: 44px; display: flex; align-items: center; gap: 10px; pointer-events: none; user-select: none;">
                <div style="line-height: 1;">
                    <span style="font-size: 21px; font-weight: 800; color: #581845; letter-spacing: -0.5px;">SMEs</span><span style="font-size: 21px; font-weight: 800; color: #d8232a; letter-spacing: -0.5px;">godigital</span>
                </div>
                <div style="height: 18px; width: 1.5px; background-color: #d0c4d8;"></div>
                <div style="line-height: 1.15;">
                    <span style="font-size: 13.5px; font-weight: 800; color: #581845; letter-spacing: -0.2px;">Pre-Approval Assistant</span>
                    <span style="display: block; font-size: 9.5px; font-weight: 700; color: #7a1d5a; text-transform: uppercase; letter-spacing: 0.5px;">IMDA Pilot</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        # Transparent click overlay covering the entire combined unit
        if st.button(" ", key="nav_logo_overlay_btn", use_container_width=False):
            st.session_state.page = "Home"
            st.session_state.show_chat_dialog = False
            st.rerun()

    for idx, page_name in enumerate(pages):
        with cols[idx + 1]:
            is_active = (current_page == page_name)
            btn_type = "primary" if is_active else "secondary"
            if st.button(page_name, key=f"nav_link_{idx}", type=btn_type, use_container_width=True):
                st.session_state.page = page_name
                st.session_state.show_chat_dialog = False
                st.rerun()

    with cols[4]:
        if st.button("Log out", key="header_logout_btn", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.show_chat_dialog = False
            st.rerun()

    st.markdown("<div style='border-bottom: 1px solid #eaeaef; margin-top: 8px; margin-bottom: 22px;'></div>", unsafe_allow_html=True)

def render_brand_header(title: str, subtitle: str = None, badge: str = "Official Prototype"):
    """Renders the top navigation header and section title."""
    render_top_navigation()
    
    badge_html = f'<span style="background: linear-gradient(135deg, #581845 0%, #d8232a 100%); color: #fff; font-size: 10px; font-weight: 700; padding: 3px 9px; border-radius: 999px; text-transform: uppercase; float: right;">{badge}</span>'
    st.markdown(f"<div>{badge_html}<h1>{title}</h1></div>", unsafe_allow_html=True)
    
    if subtitle:
        st.markdown(f"<p style='color:#636375; font-size:13px; margin-top:2px; margin-bottom:18px;'>{subtitle}</p>", unsafe_allow_html=True)

def render_hero_banner(heading: str, description: str):
    """Renders the purple-magenta mesh banner."""
    st.markdown(
        f"""
        <div style="background: linear-gradient(130deg, #3d0c3f 0%, #5d1a58 35%, #7a1d5a 70%, #9a1f52 100%); color: #ffffff; padding: 26px 28px; border-radius: 16px; margin-bottom: 24px; box-shadow: 0 10px 24px -6px rgba(61, 12, 63, 0.25);">
            <div style="font-size: 20px; font-weight: 800; color: #ffffff; margin-bottom: 6px;">{heading}</div>
            <div style="font-size: 13.5px; color: #f3d7e8; line-height: 1.5; max-width: 88%;">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def render_purple_segmented_stepper(current_step: int):
    """
    Renders the 4-step progress bar and clickable buttons strictly inside the purple banner.
    Accurately switches active steps to green when requirements are satisfied, and turns
    Step 4 green once submitted. Fixes inner-text background highlight artifacts.
    """
    steps = [
        "1. Discovery",
        "2. Checklist",
        "3. Prerequisites",
        "4. Review & Summary"
    ]

    selected_cat = st.session_state.get("selected_category")
    is_step_1_done = bool(selected_cat and str(selected_cat).strip() != "")

    cat_answers = st.session_state.get("category_answers", {})
    is_step_2_done = bool(is_step_1_done and len(cat_answers) > 0)

    from assessment_schemas import BASELINE_PREREQUISITES_SCHEMA
    assessment_data = st.session_state.get("assessment", {})
    all_baseline_keys = [
        item["key"] 
        for section in BASELINE_PREREQUISITES_SCHEMA.values() 
        for item in section 
        if item["key"] != "customer_track"
    ]
    is_step_3_done = all(assessment_data.get(k) is not None for k in all_baseline_keys)

    is_step_4_done = bool(st.session_state.get("form_submitted", False))

    completion_flags = [is_step_1_done, is_step_2_done, is_step_3_done, is_step_4_done]

    with st.container(key="stepper_isolated_container"):
        st.markdown(
            f"""
            <div style="color: #f3d7e8; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 12px;">
                Assessment Flow — Step {current_step + 1} of 4: {steps[current_step]}
            </div>
            """,
            unsafe_allow_html=True
        )

        cols = st.columns(4)
        for idx, name in enumerate(steps):
            with cols[idx]:
                is_active = (idx == current_step)
                is_done = completion_flags[idx]

                if is_done:
                    bar_color = "#00e676"
                    prefix = "✓ "
                    text_color = "#e8f5e9"
                    btn_bg = "rgba(0, 230, 118, 0.28)" if is_active else "rgba(0, 230, 118, 0.16)"
                    font_weight = "800" if is_active else "700"
                    border_color = "rgba(0, 230, 118, 0.8)" if is_active else "rgba(0, 230, 118, 0.4)"
                elif is_active:
                    bar_color = "#ff4081"
                    prefix = "● "
                    text_color = "#ffffff"
                    btn_bg = "rgba(255, 64, 129, 0.38)"
                    font_weight = "800"
                    border_color = "rgba(255, 64, 129, 0.85)"
                else:
                    bar_color = "rgba(255, 255, 255, 0.22)"
                    prefix = ""
                    text_color = "rgba(255, 255, 255, 0.65)"
                    btn_bg = "rgba(255, 255, 255, 0.08)"
                    font_weight = "600"
                    border_color = "rgba(255, 255, 255, 0.18)"

                st.markdown(
                    f'<div style="height: 7px; border-radius: 999px; background-color: {bar_color}; margin-bottom: 8px;"></div>',
                    unsafe_allow_html=True
                )

                st.markdown(
                    f"""
                    <style>
                    div.st-key-stepper_click_{idx} button {{
                        background-color: {btn_bg} !important;
                        border: 1.5px solid {border_color} !important;
                    }}
                    div.st-key-stepper_click_{idx} button p,
                    div.st-key-stepper_click_{idx} button span {{
                        background: transparent !important;
                        background-color: transparent !important;
                        color: {text_color} !important;
                        font-weight: {font_weight} !important;
                        -webkit-text-fill-color: {text_color} !important;
                        opacity: 1 !important;
                    }}
                    div.st-key-stepper_click_{idx} button:hover {{
                        background-color: rgba(255, 255, 255, 0.25) !important;
                        border-color: rgba(255, 255, 255, 0.6) !important;
                    }}
                    div.st-key-stepper_click_{idx} button:hover p,
                    div.st-key-stepper_click_{idx} button:hover span {{
                        color: #ffffff !important;
                        -webkit-text-fill-color: #ffffff !important;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(f"{prefix}{name}", key=f"stepper_click_{idx}", use_container_width=True):
                    st.session_state.assessment_step = idx
                    st.session_state.target_focus_key = None
                    st.rerun()

def render_feature_card(tag: str, title: str, description: str, icon: str = ""):
    """Renders portal cards with prominent badges and icons."""
    icon_html = f"<span style='font-size: 20px;'>{icon}</span> " if icon else ""
    st.markdown(
        f"""
        <div class="portal-card">
            <div>
                <div class="portal-card-tag">{tag}</div>
                <div class="portal-card-title">{icon_html}{title}</div>
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
