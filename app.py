import streamlit as st
import requests
import re
from urllib.parse import urljoin
from google import genai


# =========================================================
# APP CONFIG
# =========================================================

st.set_page_config(
    page_title="IMDA Pre-Approval Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# CONSTANTS
# =========================================================

BASE_URL = "https://preapproval-guide.imda.gov.sg"

CATEGORY_DIRECTORY_URL = (
    BASE_URL
    + "/pre-approval-guide/stage-1-vendor-self-assessment/"
    + "identify-suitable-solution-category.md"
)

GUIDE_HOME_URL = BASE_URL

MODEL_NAME = "gemini-3.6-flash"


# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "page": "Home",
    "assessment": {},
    "category_suggestions": [],
    "selected_category": None,
    "selected_category_url": None,
    "category_requirements": [],
    "category_answers": {},
    "chat_history": []
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
        color: #17365d;
    }

    .sub-title {
        font-size: 19px;
        color: #666;
        margin-bottom: 30px;
    }

    .hero {
        padding: 34px;
        border-radius: 16px;
        background: linear-gradient(135deg, #eef4ff, #f8fbff);
        border: 1px solid #d8e4f5;
        margin-bottom: 30px;
    }

    .feature-card {
        padding: 25px;
        border-radius: 14px;
        border: 1px solid #dedede;
        background: white;
        min-height: 195px;
    }

    .feature-title {
        font-size: 23px;
        font-weight: 650;
        margin-bottom: 12px;
    }

    .result-card {
        padding: 24px;
        border-radius: 14px;
        border: 1px solid #dedede;
        background: #fafafa;
        margin-bottom: 15px;
    }

    .small-text {
        color: #666;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# =========================================================
# DATA FUNCTIONS
# =========================================================

@st.cache_data(ttl=3600)
def fetch_text(url):
    """Fetch a text/Markdown page from the IMDA guide."""

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.text


@st.cache_data(ttl=3600)
def get_category_catalogue():
    """
    Parse the official IMDA solution-category directory.

    Returns:
        dictionary:
            {
                "Sector: Category":
                    {
                        "sector": ...,
                        "category": ...,
                        "url": ...,
                        "description": ...
                    }
            }
    """

    markdown = fetch_text(CATEGORY_DIRECTORY_URL)

    categories = {}

    current_sector = "Unknown"

    lines = markdown.splitlines()

    for line in lines:

        # Detect sector headings
        sector_match = re.search(
            r"Sector:\s*([^*]+)",
            line,
            flags=re.IGNORECASE
        )

        if sector_match:
            current_sector = sector_match.group(1).strip()

        # Detect category links
        match = re.search(
            r"\[([^\]]+)\]\(([^)]+\.md)\)",
            line
        )

        if not match:
            continue

        category_name = match.group(1).strip()
        relative_url = match.group(2).strip()

        # Ignore sector-level links
        if "/identify-suitable-solution-category/" not in relative_url:
            continue

        category_url = urljoin(
            CATEGORY_DIRECTORY_URL,
            relative_url
        )

        # Description usually follows on the next line.
        description = ""

        try:
            current_index = lines.index(line)

            for following_line in lines[current_index + 1:current_index + 5]:
                cleaned = following_line.strip()

                if cleaned and not cleaned.startswith("a)"):
                    description = cleaned
                    break

        except Exception:
            pass

        key = f"{current_sector}: {category_name}"

        categories[key] = {
            "sector": current_sector,
            "category": category_name,
            "url": category_url,
            "description": description
        }

    return categories


@st.cache_data(ttl=3600)
def get_category_requirements(category_url):
    """
    Retrieve the selected category's official requirements page
    and extract the questions.
    """

    markdown = fetch_text(category_url)

    questions = []

    lines = markdown.splitlines()

    for i, line in enumerate(lines):

        # Question heading
        q_match = re.match(
            r"###\s+Q(\d+)\s+(.*)",
            line.strip()
        )

        if not q_match:
            continue

        q_number = q_match.group(1)
        heading = q_match.group(2).strip()

        # Determine whether mandatory or preferred
        is_mandatory = "Mandatory" in heading

        # Find the Main Question
        question_text = ""

        for next_line in lines[i + 1:i + 8]:

            if "Main Question:" in next_line:

                question_text = next_line.split(
                    "Main Question:",
                    1
                )[1].strip()

                break

        if not question_text:
            continue

        questions.append(
            {
                "number": q_number,
                "heading": heading,
                "question": question_text,
                "mandatory": is_mandatory
            }
        )

    return questions


# =========================================================
# GEMINI
# =========================================================

def get_gemini_client():
    """Get Gemini client from Streamlit Cloud Secrets."""

    api_key = st.secrets["GEMINI_API_KEY"]

    return genai.Client(
        api_key=api_key
    )


def recommend_categories(vendor_description):
    """
    Ask Gemini to match the vendor's description against
    the official IMDA category catalogue.
    """

    client = get_gemini_client()

    if client is None:
        return {
            "error": "Gemini API key is not configured."
        }

    catalogue = get_category_catalogue()

    catalogue_text = "\n\n".join(
        [
            (
                f"OFFICIAL CATEGORY: {key}\n"
                f"DESCRIPTION: {value['description']}\n"
                f"URL: {value['url']}"
            )
            for key, value in catalogue.items()
        ]
    )

    system_instruction = """
You are an IMDA Pre-Approval solution-category
recommendation assistant.

Your task is to help a vendor identify potentially
relevant solution categories from the OFFICIAL IMDA
solution-category catalogue.

STRICT RULES:

1. ONLY recommend categories appearing in the catalogue.
2. NEVER invent, rename, merge or create categories.
3. Use the exact sector and category names from the catalogue.
4. Return up to 3 genuinely relevant matches.
5. Multiple matches are allowed when a vendor's solution
   reasonably covers different functions.
6. Base matching on the solution's actual functions,
   use cases, features and business purpose.
7. Do not determine formal programme eligibility.
8. Do not claim that any recommendation is confirmed.
9. If the description is insufficient, say that more
   information is needed.
10. Give a short explanation for each match.

Return ONLY this format:

MATCH
CATEGORY: <exact official category>
WHY: <one or two sentence explanation>

MATCH
CATEGORY: <exact official category>
WHY: <one or two sentence explanation>

Do not include categories that are weak or speculative.
"""

    user_prompt = f"""
VENDOR DESCRIPTION:

{vendor_description}

OFFICIAL IMDA CATEGORY CATALOGUE:

{catalogue_text}
"""

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_prompt,
            config={
                "system_instruction": system_instruction
            }
        )

        return {
            "answer": response.text,
            "catalogue": catalogue
        }

    except Exception as e:

        return {
            "error": str(e)
        }


def parse_category_matches(answer, catalogue):
    """
    Convert Gemini output into validated category matches.
    """

    results = []

    blocks = answer.split("MATCH")

    for block in blocks:

        category_match = re.search(
            r"CATEGORY:\s*(.+)",
            block
        )

        why_match = re.search(
            r"WHY:\s*(.+)",
            block,
            flags=re.DOTALL
        )

        if not category_match:
            continue

        category_text = category_match.group(1).strip()

        matched_key = None

        # Exact match first
        for key in catalogue:

            if category_text.lower() == key.lower():

                matched_key = key
                break

        # Then allow "Sector: Category" to match cleanly
        if matched_key is None:

            for key in catalogue:

                if key.lower() in category_text.lower():

                    matched_key = key
                    break

        if matched_key is None:
            continue

        why = (
            why_match.group(1).strip()
            if why_match
            else "This category appears relevant based on the description."
        )

        # Stop explanation at next MATCH if necessary
        why = why.split("MATCH")[0].strip()

        results.append(
            {
                "category_key": matched_key,
                "why": why,
                "url": catalogue[matched_key]["url"]
            }
        )

    return results[:3]


# =========================================================
# NAVIGATION
# =========================================================

pages = [
    "Home",
    "Self-Assessment",
    "AI Category Finder",
    "Category Requirements",
    "AI Assistant",
    "About Us",
    "Methodology"
]

st.sidebar.title("IMDA Pre-Approval")
st.sidebar.caption("Vendor Self-Service Assistant")

selected_page = st.sidebar.radio(
    "Navigate",
    pages,
    index=pages.index(st.session_state.page)
)

st.session_state.page = selected_page

st.sidebar.markdown("---")
st.sidebar.caption("Proof-of-Concept Prototype")


# =========================================================
# HOME
# =========================================================

if st.session_state.page == "Home":

    st.markdown(
        '<div class="main-title">IMDA Pre-Approval Assistant</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="sub-title">'
        'A smarter way for vendors to understand and navigate '
        'the IMDA Pre-Approval process.'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="hero">
            <h2>How can we help you today?</h2>
            <p>
            Check your readiness, find a relevant solution category,
            or ask questions about Pre-Approval.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)

    with col1:

        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">
                    ✅ Self-Assessment
                </div>
                <p>
                Work through a guided assessment covering
                vendor and solution eligibility requirements.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "Start Self-Assessment →",
            use_container_width=True
        ):

            st.session_state.page = "Self-Assessment"
            st.rerun()

    with col2:

        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-title">
                    🤖 Find My Solution Category
                </div>
                <p>
                Describe your solution in your own words and
                use AI to identify potentially relevant official
                IMDA solution categories.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("")

        if st.button(
            "Find a Category →",
            use_container_width=True
        ):

            st.session_state.page = "AI Category Finder"
            st.rerun()


# =========================================================
# SELF-ASSESSMENT
# =========================================================

elif st.session_state.page == "Self-Assessment":

    st.title("Vendor Self-Assessment")

    st.progress(
        0.50,
        text="Vendor and Solution Eligibility"
    )

    st.info(
        "This is a proof-of-concept self-assessment. "
        "It does not constitute an official IMDA eligibility decision."
    )

    # -----------------------------------------------------
    # Vendor Eligibility
    # -----------------------------------------------------

    st.subheader("1. Vendor Eligibility")

    vendor_questions = [

        (
            "incorporated",
            "Is your company incorporated in Singapore?",
            ["Yes", "No"]
        ),

        (
            "operation",
            "Has your company been in operation for at least 18 months?",
            ["Yes", "No"]
        ),

        (
            "financial",
            "Is your company financially stable?",
            ["Yes", "No", "Not sure"]
        ),

        (
            "track_record",
            "Does your company have satisfactory track record "
            "with government agencies?",
            [
                "Yes",
                "No",
                "Not currently, but development is underway"
            ]
        ),

        (
            "resources",
            "Does your company have sufficient quality resources?",
            ["Yes", "No", "Not sure"]
        ),

        (
            "cooling",
            "Is your company currently serving a one-year "
            "cooling period from IMDA?",
            ["Yes", "No"]
        ),

        (
            "invoice_now",
            "Has your company signed up for an InvoiceNow account?",
            [
                "Yes",
                "No",
                "Not currently, but development is underway"
            ]
        )
    ]

    for key, question, options in vendor_questions:

        value = st.radio(
            question,
            options,
            key=f"vendor_{key}"
        )

        st.session_state.assessment[key] = value

    # -----------------------------------------------------
    # Solution Track Record
    # -----------------------------------------------------

    st.subheader("2. Solution Track Record")

    industries = st.radio(
        "Select the statement that best describes the "
        "industries your solution caters to.",
        [
            "Many industries",
            "One or few industries",
            "Not sure"
        ],
        key="industries"
    )

    st.session_state.assessment["industries"] = industries

    if industries == "One or few industries":

        customer_track = st.radio(
            "Since your solution caters to a specific industry, "
            "has your solution been used by at least 5 "
            "Singapore-registered SMEs?",
            ["Yes", "No", "Not sure"],
            key="customer_track"
        )

        st.session_state.assessment[
            "customer_track"
        ] = customer_track

    # -----------------------------------------------------
    # Solution Eligibility
    # -----------------------------------------------------

    st.subheader("3. Solution Eligibility")

    solution_questions = [

        (
            "pricing",
            "Is your solution priced reasonably for SMEs?",
            ["Yes", "No", "Not sure"]
        ),

        (
            "suitability",
            "Is your solution designed to suit the needs "
            "and demands of SMEs?",
            ["Yes", "No", "Not sure"]
        ),

        (
            "productivity",
            "Does your solution help SMEs improve productivity?",
            ["Yes", "No", "Not sure"]
        ),

        (
            "website",
            "Do you have a website that showcases the solution?",
            [
                "Yes",
                "No",
                "Not currently, but development is underway"
            ]
        ),

        (
            "dapdp",
            "Have you validated your digital solution's compliance "
            "with the Data Analytics and/or Personal Data Protection "
            "Requirements?",
            [
                "Yes",
                "No",
                "Not currently, but development is underway"
            ]
        )
    ]

    for key, question, options in solution_questions:

        value = st.radio(
            question,
            options,
            key=f"solution_{key}"
        )

        st.session_state.assessment[key] = value

    st.markdown("---")

    if st.button(
        "Continue to Solution Category →",
        type="primary",
        use_container_width=True
    ):

        st.session_state.page = "AI Category Finder"
        st.rerun()


# =========================================================
# AI CATEGORY FINDER
# =========================================================

elif st.session_state.page == "AI Category Finder":

    st.title("🤖 Find Your Solution Category")

    st.write(
        "Describe your solution in your own words. "
        "Gemini will compare it against the official IMDA "
        "solution-category catalogue."
    )

    st.warning(
        "AI suggestions are for guidance only. They do not "
        "constitute confirmation of the appropriate solution "
        "category or eligibility."
    )

    description = st.text_area(
        "Tell us about your solution",
        height=180,
        value=st.session_state.assessment.get(
            "solution_description",
            ""
        ),
        placeholder=(
            "Example: We provide software development services "
            "and have developed an online test system, visitor "
            "management system and document filing system."
        )
    )

    st.session_state.assessment[
        "solution_description"
    ] = description

    if st.button(
        "Find Relevant Categories →",
        type="primary",
        use_container_width=True
    ):

        if not description.strip():

            st.error(
                "Please describe your solution first."
            )

        else:

            with st.spinner(
                "Comparing your solution against the "
                "official IMDA solution categories..."
            ):

                result = recommend_categories(
                    description
                )

            if "error" in result:

                st.error(
                    result["error"]
                )

            else:

                matches = parse_category_matches(
                    result["answer"],
                    result["catalogue"]
                )

                st.session_state.category_suggestions = matches

    if st.session_state.category_suggestions:

        st.markdown("---")

        st.subheader(
            "Potentially Relevant IMDA Solution Categories"
        )

        for index, suggestion in enumerate(
            st.session_state.category_suggestions
        ):

            category_key = suggestion["category_key"]

            category = get_category_catalogue()[
                category_key
            ]

            with st.container(border=True):

                st.markdown(
                    f"### {index + 1}. {category_key}"
                )

                st.write(
                    suggestion["why"]
                )

                if st.button(
                    "Select this category",
                    key=f"select_category_{index}",
                    use_container_width=True
                ):

                    st.session_state.selected_category = category_key

                    st.session_state.selected_category_url = (
                        category["url"]
                    )

                    st.session_state.page = (
                        "Category Requirements"
                    )

                    st.rerun()


# =========================================================
# CATEGORY REQUIREMENTS
# =========================================================

elif st.session_state.page == "Category Requirements":

    st.title("Category Requirements")

    selected = st.session_state.selected_category

    if not selected:

        st.info(
            "Select a solution category first."
        )

        if st.button("← Back to Category Finder"):

            st.session_state.page = "AI Category Finder"
            st.rerun()

    else:

        category = get_category_catalogue()[selected]

        st.success(
            f"Selected category: {selected}"
        )

        st.write(
            category["description"]
        )

        st.link_button(
            "Open official IMDA requirements page",
            category["url"]
        )

        st.markdown("---")

        with st.spinner(
            "Loading the official category requirements..."
        ):

            requirements = get_category_requirements(
                category["url"]
            )

        mandatory = [
            q for q in requirements
            if q["mandatory"]
        ]

        preferred = [
            q for q in requirements
            if not q["mandatory"]
        ]

        if not mandatory:

            st.warning(
                "The category requirements could not be "
                "parsed automatically. Please use the official "
                "requirements link above."
            )

        else:

            st.subheader(
                "Mandatory Requirements"
            )

            st.caption(
                "Mandatory questions must be answered Yes "
                "to continue according to the official category page."
            )

            for question in mandatory:

                key = (
                    f"category_q_{question['number']}"
                )

                answer = st.radio(
                    f"Q{question['number']} — "
                    f"{question['question']}",
                    ["Yes", "No", "Not sure"],
                    key=key
                )

                st.session_state.category_answers[
                    question["number"]
                ] = answer

            if preferred:

                with st.expander(
                    f"View {len(preferred)} preferred requirements"
                ):

                    for question in preferred:

                        st.write(
                            f"Q{question['number']} — "
                            f"{question['question']}"
                        )

            st.markdown("---")

            if st.button(
                "Generate Preliminary Result →",
                type="primary",
                use_container_width=True
            ):

                st.session_state.page = "AI Assistant"
                st.rerun()


# =========================================================
# AI ASSISTANT
# =========================================================

elif st.session_state.page == "AI Assistant":

    st.title("💬 Pre-Approval AI Assistant")

    st.write(
        "Ask questions about your assessment, the selected "
        "solution category, or the Pre-Approval process."
    )

    selected = st.session_state.selected_category

    if selected:

        st.info(
            f"Assessment context: **{selected}**"
        )

    # -----------------------------------------------------
    # Preliminary assessment summary
    # -----------------------------------------------------

    if st.session_state.assessment:

        st.subheader(
            "Your Preliminary Assessment"
        )

        assessment = st.session_state.assessment

        blockers = []
        in_progress = []
        uncertain = []

        for key, value in assessment.items():

            if isinstance(value, str):

                if value == "No":
                    blockers.append(
                        key.replace("_", " ").title()
                    )

                elif value == (
                    "Not currently, but development is underway"
                ):
                    in_progress.append(
                        key.replace("_", " ").title()
                    )

                elif value in [
                    "Not sure",
                    "Many industries",
                    "One or few industries",
                    "Yes"
                ]:
                    pass

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Potential gaps",
                len(blockers)
            )

        with col2:
            st.metric(
                "In progress",
                len(in_progress)
            )

        with col3:
            st.metric(
                "AI context",
                "Ready"
            )

        if blockers:

            st.error(
                "Potential gaps identified: "
                + ", ".join(blockers)
            )

        if in_progress:

            st.warning(
                "Items marked as in development: "
                + ", ".join(in_progress)
            )

    # -----------------------------------------------------
    # Chat history
    # -----------------------------------------------------

    for message in st.session_state.chat_history:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )

    prompt = st.chat_input(
        "e.g. Why does this requirement matter?"
    )

    if prompt:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.write(prompt)

        client = get_gemini_client()

        if client is None:

            response_text = (
                "Gemini is not configured for this application."
            )

        else:

            selected_context = ""

            if selected:

                category = get_category_catalogue()[
                    selected
                ]

                selected_context = f"""
SELECTED SOLUTION CATEGORY:

{selected}

OFFICIAL CATEGORY DESCRIPTION:

{category['description']}
"""

            assessment_context = (
                str(st.session_state.assessment)
            )

            category_context = (
                str(st.session_state.category_answers)
            )

            prompt_for_model = f"""
You are an AI assistant supporting vendors using
the IMDA Pre-Approval self-service prototype.

Use the official IMDA category information below
and the vendor's assessment context.

Do not make an official eligibility decision.

Do not invent requirements.

Explain things clearly and practically.

{selected_context}

VENDOR ASSESSMENT CONTEXT:

{assessment_context}

CATEGORY ASSESSMENT CONTEXT:

{category_context}

VENDOR QUESTION:

{prompt}

Answer the vendor's question.
"""

            try:

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=prompt_for_model
                )

                response_text = response.text

            except Exception as e:

                response_text = (
                    "I couldn't complete the AI response "
                    f"because of this error: {e}"
                )

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": response_text
            }
        )

        with st.chat_message("assistant"):

            st.write(response_text)


# =========================================================
# ABOUT US
# =========================================================

elif st.session_state.page == "About Us":

    st.title("About This Project")

    st.write(
        """
        The IMDA Pre-Approval Assistant is a proof-of-concept
        designed to improve the vendor self-service experience.

        The concept combines guided self-assessment with
        GenAI-powered solution-category recommendation and
        conversational assistance.
        """
    )

    st.subheader("Problem")

    st.write(
        """
        Vendors frequently seek meetings or write to IMDA
        for clarification on requirements that are already
        available in the Pre-Approval Guide.

        The project explores how GenAI can make this information
        easier to understand and navigate through a single
        self-service experience.
        """
    )

    st.subheader("Core AI Use Cases")

    st.write(
        """
        **1. Solution Category Recommendation**

        Match a vendor's natural-language description against
        the official IMDA solution-category directory.

        **2. Conversational Assistance**

        Allow vendors to ask questions about their assessment
        and the Pre-Approval journey.
        """
    )


# =========================================================
# METHODOLOGY
# =========================================================

elif st.session_state.page == "Methodology":

    st.title("Methodology")

    st.subheader("1. Vendor Self-Assessment")

    st.code(
        """
Vendor information
        ↓
Vendor eligibility
        ↓
Solution track record
        ↓
Solution eligibility
        ↓
Solution description
        """
    )

    st.subheader("2. GenAI Solution Category Recommendation")

    st.code(
        """
Vendor description
        ↓
Official IMDA category directory
        ↓
Gemini Flash
        ↓
Semantic matching
        ↓
Up to 3 potential categories
        ↓
Vendor selects category
        """
    )

    st.subheader("3. Category Requirements")

    st.code(
        """
Selected category
        ↓
Official IMDA category page
        ↓
Mandatory requirements
        ↓
Vendor answers
        ↓
Preliminary gaps
        """
    )

    st.subheader("4. Conversational Assistant")

    st.code(
        """
Vendor question
        +
Assessment context
        +
Selected category
        ↓
Gemini Flash
        ↓
Contextual explanation
        """
    )

    st.subheader("Primary Data Source")

    st.write(
        "Official IMDA Pre-Approval Guide"
    )

    st.write(
        CATEGORY_DIRECTORY_URL
    )


# =========================================================
# GLOBAL DISCLAIMER
# =========================================================

st.markdown("---")

with st.expander(
    "⚠️ IMPORTANT NOTICE — Proof-of-Concept Prototype"
):

    st.write(
        """
        This web application is developed as a proof-of-concept prototype.
        The information provided here is NOT intended for actual usage
        and should not be relied upon for making any decisions,
        especially those related to financial, legal, or healthcare matters.

        Furthermore, please be aware that the LLM may generate inaccurate
        or incorrect information. You assume full responsibility for how
        you use any generated output.

        Always consult qualified professionals for accurate and
        personalised advice.
        """
    )