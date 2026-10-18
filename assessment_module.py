# =========================================================
# STEP 3: BASELINE PREREQUISITE VALIDATION
# =========================================================

def render_step_3_prerequisites():
    st.markdown("### 🏢 Step 3: Baseline Prerequisite Validation")
    st.caption("Confirm foundational corporate, financial, and deployment prerequisites with real-time feedback.")

    if st.session_state.get("selected_category"):
        st.info(f"Target Category: **{st.session_state.selected_category}**")

    # --- PURPLE SEGMENTED TAB STRIP ---
    tab_names = [
        "1. Corporate & Financials", 
        "2. SME Deployment Track Record", 
        "3. Solution Suitability"
    ]
    current_tab_idx = st.session_state.get("prereq_tab_idx", 0)

    with st.container(key="prereq_subtab_bar"):
        tcols = st.columns(3)
        for t_idx, t_name in enumerate(tab_names):
            with tcols[t_idx]:
                is_active_tab = (t_idx == current_tab_idx)
                
                if is_active_tab:
                    tab_bg = "linear-gradient(130deg, #581845 0%, #7a1d5a 50%, #9a1f52 100%)"
                    tab_text = "#ffffff"
                    tab_shadow = "0 4px 12px rgba(88, 24, 69, 0.25)"
                else:
                    tab_bg = "transparent"
                    tab_text = "#581845"
                    tab_shadow = "none"

                st.markdown(
                    f"""
                    <style>
                    div.st-key-subtab_btn_{t_idx} button,
                    div.st-key-subtab_btn_{t_idx} button p,
                    div.st-key-subtab_btn_{t_idx} button span {{
                        background: {tab_bg} !important;
                        color: {tab_text} !important;
                        -webkit-text-fill-color: {tab_text} !important;
                        box-shadow: {tab_shadow} !important;
                    }}
                    div.st-key-subtab_btn_{t_idx} button:hover,
                    div.st-key-subtab_btn_{t_idx} button:hover p,
                    div.st-key-subtab_btn_{t_idx} button:hover span {{
                        color: {'#ffffff' if is_active_tab else '#7a1d5a'} !important;
                        -webkit-text-fill-color: {'#ffffff' if is_active_tab else '#7a1d5a'} !important;
                    }}
                    </style>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(t_name, key=f"subtab_btn_{t_idx}", use_container_width=True):
                    st.session_state.prereq_tab_idx = t_idx
                    st.session_state.target_focus_key = None
                    st.rerun()

    target_focus = st.session_state.get("target_focus_key")

    # 1. Corporate & Financials
    if st.session_state.prereq_tab_idx == 0:
        for item in BASELINE_PREREQUISITES_SCHEMA["corporate"]:
            k = item["key"]
            is_focused = (target_focus == f"prereq_{k}")

            st.markdown(f'<div id="anchor_prereq_{k}"></div>', unsafe_allow_html=True)
            with st.container(border=True):
                if is_focused:
                    st.markdown(
                        """
                        <div style='background-color: #fff0f0; border-left: 4px solid #d8232a; padding: 6px 10px; margin-bottom: 8px; border-radius: 4px;'>
                            <strong style='color: #d8232a; font-size: 12px;'>👉 Focus: Please update this prerequisite</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                current_val = st.session_state.assessment.get(k)
                idx = item["options"].index(current_val) if current_val in item["options"] else None

                b_col1, b_col2 = st.columns([5.2, 1.8])
                with b_col1:
                    st.markdown(f"**{item['question']}**")
                with b_col2:
                    render_compliance_badge(current_val, item["compliant_values"])

                chosen = st.radio(
                    f"Radio for {k}",
                    item["options"],
                    index=idx,
                    key=f"vendor_{k}",
                    label_visibility="collapsed"
                )
                if chosen is not None and chosen != current_val:
                    st.session_state.assessment[k] = chosen
                    st.session_state.target_focus_key = None
                    st.rerun()

    # 2. Deployment Track Record
    elif st.session_state.prereq_tab_idx == 1:
        ind_item = BASELINE_PREREQUISITES_SCHEMA["deployment"][0]
        ind_k = ind_item["key"]
        is_ind_focused = (target_focus == f"prereq_{ind_k}")

        st.markdown(f'<div id="anchor_prereq_{ind_k}"></div>', unsafe_allow_html=True)
        with st.container(border=True):
            if is_ind_focused:
                st.markdown(
                    """
                    <div style='background-color: #fff0f0; border-left: 4px solid #d8232a; padding: 6px 10px; margin-bottom: 8px; border-radius: 4px;'>
                        <strong style='color: #d8232a; font-size: 12px;'>👉 Focus: Please update this prerequisite</strong>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            current_ind = st.session_state.assessment.get(ind_k)
            ind_idx = ind_item["options"].index(current_ind) if current_ind in ind_item["options"] else None

            bi_col1, bi_col2 = st.columns([5.2, 1.8])
            with bi_col1:
                st.markdown(f"**{ind_item['question']}**")
            with bi_col2:
                render_compliance_badge(current_ind, ind_item["compliant_values"])

            chosen_ind = st.radio(
                f"Radio for {ind_k}",
                ind_item["options"],
                index=ind_idx,
                key=f"vendor_{ind_k}",
                label_visibility="collapsed"
            )
            if chosen_ind is not None and chosen_ind != current_ind:
                st.session_state.assessment[ind_k] = chosen_ind
                st.session_state.target_focus_key = None
                st.rerun()

        if st.session_state.assessment.get("industries") == "One or few industries":
            cust_item = BASELINE_PREREQUISITES_SCHEMA["deployment"][1]
            cust_k = cust_item["key"]
            is_cust_focused = (target_focus == f"prereq_{cust_k}")

            st.markdown(f'<div id="anchor_prereq_{cust_k}"></div>', unsafe_allow_html=True)
            with st.container(border=True):
                if is_cust_focused:
                    st.markdown(
                        """
                        <div style='background-color: #fff0f0; border-left: 4px solid #d8232a; padding: 6px 10px; margin-bottom: 8px; border-radius: 4px;'>
                            <strong style='color: #d8232a; font-size: 12px;'>👉 Focus: Please update this prerequisite</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                current_track = st.session_state.assessment.get(cust_k)
                track_idx = cust_item["options"].index(current_track) if current_track in cust_item["options"] else None

                bt_col1, bt_col2 = st.columns([5.2, 1.8])
                with bt_col1:
                    st.markdown(f"**{cust_item['question']}**")
                with bt_col2:
                    render_compliance_badge(current_track, cust_item["compliant_values"])

                chosen_track = st.radio(
                    f"Radio for {cust_k}",
                    cust_item["options"],
                    index=track_idx,
                    key=f"vendor_{cust_k}",
                    label_visibility="collapsed"
                )
                if chosen_track is not None and chosen_track != current_track:
                    st.session_state.assessment[cust_k] = chosen_track
                    st.session_state.target_focus_key = None
                    st.rerun()

    # 3. Solution Suitability
    elif st.session_state.prereq_tab_idx == 2:
        for item in BASELINE_PREREQUISITES_SCHEMA["solution"]:
            sk = item["key"]
            is_sol_focused = (target_focus == f"prereq_{sk}")

            st.markdown(f'<div id="anchor_prereq_{sk}"></div>', unsafe_allow_html=True)
            with st.container(border=True):
                if is_sol_focused:
                    st.markdown(
                        """
                        <div style='background-color: #fff0f0; border-left: 4px solid #d8232a; padding: 6px 10px; margin-bottom: 8px; border-radius: 4px;'>
                            <strong style='color: #d8232a; font-size: 12px;'>👉 Focus: Please update this prerequisite</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                current_val = st.session_state.assessment.get(sk)
                idx = item["options"].index(current_val) if current_val in item["options"] else None

                bs_col1, bs_col2 = st.columns([5.2, 1.8])
                with bs_col1:
                    st.markdown(f"**{item['question']}**")
                with bs_col2:
                    render_compliance_badge(current_val, item["compliant_values"])

                chosen_sol = st.radio(
                    f"Radio for {sk}",
                    item["options"],
                    index=idx,
                    key=f"solution_{sk}",
                    label_visibility="collapsed"
                )
                if chosen_sol is not None and chosen_sol != current_val:
                    st.session_state.assessment[sk] = chosen_sol
                    st.session_state.target_focus_key = None
                    st.rerun()

    if target_focus and target_focus.startswith("prereq_"):
        st.markdown(
            f"""
            <script>
                setTimeout(function() {{
                    var el = document.getElementById("anchor_{target_focus}");
                    if (el) {{
                        el.scrollIntoView({{ behavior: 'smooth', block: 'center' }});
                    }}
                }}, 250);
            </script>
            """,
            unsafe_allow_html=True
        )

    st.markdown("")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("← Back to Step 2: Category Checklist", use_container_width=True):
            st.session_state.assessment_step = 1
            st.session_state.target_focus_key = None
            st.rerun()
    with col_b2:
        if st.button("Proceed to Step 4: Review & Summary →", type="primary", use_container_width=True):
            st.session_state.assessment_step = 3
            st.session_state.target_focus_key = None
            st.rerun()
