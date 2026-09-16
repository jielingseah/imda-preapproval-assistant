
import streamlit as st

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="IMDA Pre-Approval Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# CUSTOM CSS
# ---------------------------------------------------------
st.markdown("""
<style>

    .main-title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .sub-title {
        font-size: 20px;
        color: #666;
        margin-bottom: 30px;
    }

    .hero-box {
        padding: 35px;
        border-radius: 16px;
        background: linear-gradient(135deg, #eef4ff, #f8fbff);
        border: 1px solid #dbe5f5;
        margin-bottom: 30px;
    }

    .card {
        padding: 25px;
        border-radius: 14px;
        border: 1px solid #ddd;
        background: white;
        min-height: 220px;
    }

    .card-title {
        font-size: 24px;
        font-weight: 650;
        margin-bottom: 10px;
    }

    .card-text {
        font-size: 16px;
        color: #555;
        line-height: 1.6;
    }

    .section-title {
        font-size: 30px;
        font-weight: 700;
        margin-top: 20px;
    }

    .small-note {
        color: #666;
        font-size: 14px;
    }

</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("IMDA Pre-Approval")
st.sidebar.caption("Vendor Self-Service Assistant")

page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Self-Assessment",
        "AI Assistant",
        "About Us",
        "Methodology"
    ]
)

st.sidebar.markdown("---")
st.sidebar.caption("Proof-of-Concept Prototype")

# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------
if page == "Home":

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

    st.markdown("""
    <div class="hero-box">
        <h2>How can we help you today?</h2>
        <p>
        Check your readiness, understand the requirements,
        or ask questions about the Pre-Approval process.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("""
        <div class="card">
            <div class="card-title">✅ Self-Assessment</div>
            <div class="card-text">
                Answer a series of guided questions to understand
                whether your company and solution appear to meet
                the relevant Pre-Approval requirements.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        if st.button(
            "Start Self-Assessment →",
            use_container_width=True
        ):
            st.session_state["page"] = "Self-Assessment"
            st.rerun()

    with col2:

        st.markdown("""
        <div class="card">
            <div class="card-title">💬 Ask the Assistant</div>
            <div class="card-text">
                Ask questions about eligibility, solution categories,
                application requirements and the Pre-Approval journey.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.write("")

        if st.button(
            "Ask a Question →",
            use_container_width=True
        ):
            st.session_state["page"] = "AI Assistant"
            st.rerun()

    st.markdown("---")

    st.markdown(
        '<div class="section-title">One place to get started</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        Instead of searching through multiple pages or writing to IMDA
        for routine clarification, vendors can use this assistant to
        assess their readiness and find relevant guidance.
        """
    )

# ---------------------------------------------------------
# SELF-ASSESSMENT
# ---------------------------------------------------------
elif page == "Self-Assessment":

    st.markdown(
        '<div class="section-title">Vendor Self-Assessment</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Answer the questions below to perform a preliminary assessment."
    )

    st.info(
        "This is a proof-of-concept assessment. "
        "It does not constitute an official IMDA eligibility decision."
    )

    st.markdown("### 1. Are you applying as a technology solution vendor?")

    q1 = st.radio(
        "Select one:",
        ["Yes", "No", "Not sure"],
        key="q1"
    )

    st.markdown("### 2. Does your solution fall within an eligible solution category?")

    q2 = st.radio(
        "Select one:",
        ["Yes", "No", "Not sure"],
        key="q2"
    )

    st.markdown("### 3. Have your customers used the solution for the required period?")

    q3 = st.radio(
        "Select one:",
        ["Yes", "No", "Not sure"],
        key="q3"
    )

    st.markdown("---")

    if st.button("Check Preliminary Result", type="primary"):

        answers = [q1, q2, q3]

        if "No" in answers:

            st.error(
                "Potential eligibility gap identified."
            )

            st.write(
                """
                One or more answers indicate that you may not currently
                meet a relevant requirement. Review the applicable
                requirements in the Pre-Approval Guide or ask the
                AI Assistant for more information.
                """
            )

        elif "Not sure" in answers:

            st.warning(
                "More information may be required."
            )

            st.write(
                """
                Your answers indicate that you may need to clarify
                one or more requirements.
                """
            )

        else:

            st.success(
                "No obvious gap identified based on your answers."
            )

            st.write(
                """
                Based on these preliminary answers, no immediate
                eligibility gap was identified. You should still
                review the detailed requirements before applying.
                """
            )

        st.markdown("---")

        st.markdown("### Need clarification?")

        if st.button("Ask the AI Assistant about my result"):

            st.info(
                "The AI Assistant will be connected to your assessment "
                "in the next version."
            )

# ---------------------------------------------------------
# AI ASSISTANT
# ---------------------------------------------------------
elif page == "AI Assistant":

    st.markdown(
        '<div class="section-title">💬 Pre-Approval AI Assistant</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Ask a question about the IMDA Pre-Approval process."
    )

    st.info(
        "The AI knowledge base will be connected to the "
        "Pre-Approval Guide in the next version."
    )

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input(
        "e.g. Can my company apply for Pre-Approval?"
    )

    if prompt:

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.write(prompt)

        response = (
            "This is the prototype assistant. "
            "In the next version, I will search the official "
            "IMDA Pre-Approval Guide and provide a grounded answer "
            "with the relevant source."
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        with st.chat_message("assistant"):
            st.write(response)

# ---------------------------------------------------------
# ABOUT US
# ---------------------------------------------------------
elif page == "About Us":

    st.markdown(
        '<div class="section-title">About This Project</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        The IMDA Pre-Approval Assistant is a proof-of-concept project
        designed to improve the vendor self-service experience.

        The project aims to transform the existing Pre-Approval Guide
        from a primarily information-based resource into an interactive
        journey where vendors can assess their readiness and obtain
        contextual answers to their questions.
        """
    )

    st.markdown("### Objectives")

    st.write("""
    - Reduce repetitive vendor enquiries.
    - Reduce unnecessary meeting requests for routine queries.
    - Help vendors understand requirements before approaching IMDA.
    - Provide a consistent self-service experience.
    - Demonstrate how LLM technology can enhance an existing process.
    """)

    st.markdown("### Key Features")

    st.write("""
    **1. Guided Self-Assessment**

    Helps vendors identify potential eligibility gaps.

    **2. AI Assistant**

    Allows vendors to ask questions in natural language.

    **3. Integrated Experience**

    Assessment results can eventually be carried into the AI
    conversation so vendors can ask why a requirement matters
    or what they should do next.
    """)

# ---------------------------------------------------------
# METHODOLOGY
# ---------------------------------------------------------
elif page == "Methodology":

    st.markdown(
        '<div class="section-title">Methodology</div>',
        unsafe_allow_html=True
    )

    st.write(
        """
        The application uses an LLM-based retrieval approach to provide
        grounded answers using content from the official IMDA
        Pre-Approval Guide.
        """
    )

    st.markdown("### Proposed Architecture")

    st.code("""
Pre-Approval Guide
        ↓
Content extraction
        ↓
Text cleaning & chunking
        ↓
Embeddings
        ↓
Vector database
        ↓
Relevant content retrieval
        ↓
LLM
        ↓
Grounded response
        ↓
Vendor
""")

    st.markdown("### Self-Assessment Flow")

    st.code("""
Vendor
  ↓
Answer questions
  ↓
Evaluate requirements
  ↓
Identify potential gaps
  ↓
Explain result
  ↓
Ask follow-up question
  ↓
AI Assistant
""")

    st.markdown("### Chat Flow")

    st.code("""
Vendor question
      ↓
Retrieve relevant guide content
      ↓
LLM interprets retrieved content
      ↓
Generate answer
      ↓
Show supporting source
""")

# ---------------------------------------------------------
# REQUIRED DISCLAIMER
# ---------------------------------------------------------
st.markdown("---")

with st.expander("⚠️ IMPORTANT NOTICE — Proof-of-Concept"):

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
