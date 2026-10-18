# 1. Main Page Hero Search Bar
    with st.container(border=True):
        st.markdown("<h4 style='font-weight:700; color:#2b0b2e; margin:0 0 6px 0;'>🔍 Search Official Pre-Approved Categories & Solutions</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:12.5px; color:#636375; margin-bottom:12px;'>Enter keywords or describe your software in natural language to let our AI match you with eligible categories.</p>", unsafe_allow_html=True)
        
        # Check if an example prompt was clicked
        current_input_val = st.session_state.get("home_search_fill", "")

        home_search_col1, home_search_col2 = st.columns([5, 1.2])
        with home_search_col1:
            home_query = st.text_input(
                "Search query",
                value=current_input_val,
                placeholder='e.g., "Our solution helps manage pre-school operations" or "We manage SEO/SEM digital marketing campaigns"',
                label_visibility="collapsed",
                key="home_hero_search_input"
            )
        with home_search_col2:
            if st.button("Find Solution →", type="primary", use_container_width=True):
                search_val = home_query.strip() if home_query else current_input_val.strip()
                if search_val:
                    st.session_state.assessment["solution_description"] = search_val
                    st.session_state.page = "AI Category Finder"
                    st.rerun()

        # Clickable quick-fill prompt suggestions underneath
        st.markdown("<p style='font-size:11.5px; color:#777788; margin-top:8px; margin-bottom:4px;'>💡 Or click a sample prompt to try:</p>", unsafe_allow_html=True)
        s_col1, s_col2, s_col3 = st.columns(3)
        with s_col1:
            if st.button("🏫 Pre-School Operations", key="sample_prompt_1", use_container_width=True):
                st.session_state.assessment["solution_description"] = "My solution helps manage pre-school operations, student attendance, parent communications, and fee collection."
                st.session_state.page = "AI Category Finder"
                st.rerun()
        with s_col2:
            if st.button("📈 SEO/SEM Digital Marketing", key="sample_prompt_2", use_container_width=True):
                st.session_state.assessment["solution_description"] = "My solution manages SEO/SEM digital marketing campaigns, keyword bidding, and client conversion analytics."
                st.session_state.page = "AI Category Finder"
                st.rerun()
        with s_col3:
            if st.button("🔒 Cloud Cybersecurity", key="sample_prompt_3", use_container_width=True):
                st.session_state.assessment["solution_description"] = "My solution provides endpoint anti-malware, firewall protection, and automated threat detection for SME laptops."
                st.session_state.page = "AI Category Finder"
                st.rerun()
