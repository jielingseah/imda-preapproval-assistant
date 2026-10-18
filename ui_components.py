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

        /* Remove default Streamlit top blank space */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 3rem !important;
            max-width: 95% !important;
        }

        /* Universal Font Sync */
        html, body, [class*="css"], [class*="st-"], 
        h1, h2, h3, h4, h5, h6, p, div, span, label, input, textarea, button, a {
            font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
            letter-spacing: -0.01em;
        }

        html {
            scroll-behavior: smooth !important;
        }

        [data-testid="stSidebar"] {
            display: none !important;
        }
        header {visibility: hidden;}

        /* Sleek Top Government Masthead & Interactive Expandable Drawer */
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

        /* Seamless Invisible Logo Overlay */
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

        /* Sleek Deep Purple Logout Pill */
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

        /* True Fixed Floating Anchor Buttons (Bottom Right) */
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
        div.st-key-floating_chat_button button:hover {
            transform: scale(1.04) translateY(-2px) !important;
            box-shadow: 0 12px 30px rgba(88, 24, 69, 0.45) !important;
        }

        /* Prominent Step Badges */
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

        /* Portal Cards */
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
            font-size: 18px !important;
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

        /* Footer Prototype Notice */
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
    """Renders the top navigation bar with the expandable official SG banner and clickable logo."""
    pages = [
        "Pre-Approval Assessment",
        "About Us",
        "Methodology"
    ]

    current_page = st.session_state.get("page", "Home")

    # Interactive Singapore Government Masthead
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

    # Columns: Brand Logo (3.6) + 3 Nav items (2.5, 1.3, 1.4) + Logout Pill (1.0)
    cols = st.columns([3.6, 2.5, 1.3, 1.4, 1.0])

    with cols[0]:
        st.markdown(
            """
            <div style="height: 38px; padding-top: 4px; pointer-events: none;">
                <span style="font-size: 22px; font-weight: 800; color: #581845; letter-spacing: -0.5px;">SMEs</span><span style="font-size: 22px; font-weight: 800; color: #d8232a; letter-spacing: -0.5px;">godigital ↗</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button(" ", key="nav_logo_overlay_btn"):
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

def render_purple_segmented_stepper(current_step: int):
    """
    Renders an all-in-one 4-step progress bar inside the purple banner.
    Completed steps appear in bright green with checkmarks, the active step
    appears in vibrant coral, and upcoming steps appear dimmed.
    """
    steps = [
        "1. Discovery",
        "2. Checklist",
        "3. Prerequisites",
        "4. Review & Summary"
    ]

    is_step_1_done = bool(st.session_state.get("selected_category"))
    is_step_2_done = bool(st.session_state.get("category_answers"))
    is_step_3_done = bool(st.session_state.get("assessment"))

    completion_flags = [is_step_1_done, is_step_2_done, is_step_3_done, False]

    # Build unindented HTML strings to prevent Markdown code block interpretation
    bar_html_parts = []
    for idx, name in enumerate(steps):
        is_completed = (idx < current_step) or completion_flags[idx]
        is_current = (idx == current_step)

        if is_current:
            bar_color = "#ff4081"
            opacity = "1.0"
            label_color = "#ffffff"
            font_weight = "800"
            prefix = "● "
        elif is_completed:
            bar_color = "#00e676"
            opacity = "1.0"
            label_color = "#e8f5e9"
            font_weight = "700"
            prefix = "✓ "
        else:
            bar_color = "#ffffff"
            opacity = "0.22"
            label_color = "rgba(243, 215, 232, 0.55)"
            font_weight = "500"
            prefix = ""

        glow = "box-shadow: 0 0 10px rgba(0, 230, 118, 0.4);" if (is_completed and not is_current) else ""

        part = (
            f'<div style="flex: 1; margin: 0 6px; text-align: left;">'
            f'<div style="height: 10px; border-radius: 999px; background-color: {bar_color}; opacity: {opacity}; {glow}"></div>'
            f'<div style="color: {label_color}; font-size: 12.5px; font-weight: {font_weight}; margin-top: 8px;">{prefix}{name}</div>'
            f'</div>'
        )
        bar_html_parts.append(part)

    bars_layout = "".join(bar_html_parts)

    stepper_html = (
        f'<div style="background: linear-gradient(130deg, #3d0c3f 0%, #5d1a58 35%, #7a1d5a 70%, #9a1f52 100%); '
        f'border-radius: 16px; padding: 22px 24px 20px 24px; margin-bottom: 16px; '
        f'box-shadow: 0 10px 24px -6px rgba(61, 12, 63, 0.25);">'
        f'<div style="color: #f3d7e8; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 14px;">'
        f'Assessment Flow — Step {current_step + 1} of 4: {steps[current_step]}'
        f'</div>'
        f'<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
        f'{bars_layout}'
        f'</div>'
        f'</div>'
    )

    st.markdown(stepper_html, unsafe_allow_html=True)

    cols = st.columns(4)
    for idx, name in enumerate(steps):
        with cols[idx]:
            btn_type = "primary" if idx == current_step else "secondary"
            clean_lbl = name.split(". ")[1]
            if st.button(f"Go to {clean_lbl}", key=f"nav_step_bar_btn_{idx}", type=btn_type, use_container_width=True):
                st.session_state.assessment_step = idx
                st.session_state.target_focus_key = None
                st.rerun()

def render_feature_card(tag: str, title: str, description: str, icon: str = ""):
    """Renders portal cards with prominent badges and icons."""
    icon_html = f"<span style='font-size: 22px;'>{icon}</span> " if icon else ""
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
