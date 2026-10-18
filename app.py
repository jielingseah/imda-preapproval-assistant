if st.session_state.get("user_role") == "Admin":
    # High-contrast Branded Header with specific CSS override
    st.markdown(
        """
        <style>
            #admin-header-card, #admin-header-card * {
                color: #ffffff !important;
            }
            #admin-header-card h2 {
                color: #ffffff !important;
                font-size: 24px !important;
                font-weight: 800 !important;
                margin: 8px 0 6px 0 !important;
                letter-spacing: -0.3px !important;
            }
            #admin-header-card p {
                color: #f8fafc !important;
                font-size: 13.5px !important;
                margin: 0 !important;
                opacity: 0.95 !important;
            }
            #admin-header-card .admin-badge {
                background: rgba(255, 255, 255, 0.2) !important;
                color: #ffffff !important;
                font-size: 11px !important;
                font-weight: 800 !important;
                padding: 4px 10px !important;
                border-radius: 6px !important;
                display: inline-block !important;
                letter-spacing: 0.8px !important;
            }
        </style>

        <div id="admin-header-card" style="background: linear-gradient(135deg, #2b0b2e 0%, #4a154b 60%, #611f69 100%); padding: 24px 30px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 4px 14px rgba(43, 11, 46, 0.25);">
            <span class="admin-badge">SYSTEM ADMINISTRATOR</span>
            <h2>🛡️ IMDA Officer Operations & Pipeline Console</h2>
            <p>Manage daily knowledge harvesting automation, category intake governance, and audit vendor submissions.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
