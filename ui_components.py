/* =========================================================
           PURPLE THEME FOR ASSESSMENT FLOW (PROGRESS BAR & RADIO)
           ========================================================= */
        
        /* 1. Progress Bar Fill - Gradient matching hero banner */
        div[data-testid="stProgressBar"] > div > div > div > div {
            background: linear-gradient(130deg, #3d0c3f 0%, #5d1a58 35%, #7a1d5a 70%, #9a1f52 100%) !important;
            border-radius: 999px !important;
        }

        /* Progress Bar Track (Background groove) */
        div[data-testid="stProgressBar"] > div > div > div {
            background-color: #f3e8f0 !important;
            border-radius: 999px !important;
            height: 10px !important;
        }

        /* Progress text label */
        div[data-testid="stProgressBar"] + div, 
        div[data-testid="stProgressBar"] [data-testid="stMarkdownContainer"] p {
            color: #581845 !important;
            font-weight: 700 !important;
            font-size: 13px !important;
        }

        /* 2. Step Radio Buttons - Custom Purple/Magenta Active State */
        div[data-testid="stRadio"] label[data-baseweb="radio"] input:checked + div {
            background-color: #7a1d5a !important;
            border-color: #581845 !important;
        }

        /* Radio inner dot when active */
        div[data-testid="stRadio"] label[data-baseweb="radio"] input:checked + div > div {
            background-color: #ffffff !important;
        }

        /* Radio option hover ring */
        div[data-testid="stRadio"] label[data-baseweb="radio"]:hover div {
            border-color: #9a1f52 !important;
        }

        /* Radio label text styling when active */
        div[data-testid="stRadio"] label[data-baseweb="radio"]:has(input:checked) p {
            color: #581845 !important;
            font-weight: 800 !important;
        }
