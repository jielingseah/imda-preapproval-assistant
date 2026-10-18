"""
Assessment Module for IMDA Pre-Approval Assistant.
Encapsulates:
- Step 1: Category Discovery & Feasibility Pre-Check
- Step 2: Category Functional Checklist (with real-time compliance badges & deep-link focus)
- Step 3: Baseline Prerequisite Validation (with subtab selection & deep-link focus)
- Step 4: Readiness Review, Gap Audit & Stage 2 / VMP Handover
"""

import streamlit as st
import requests
import re
import time
from urllib.parse import urljoin
from google import genai
from google.genai import types

from imda_knowledge import (
    MODEL_NAME,
    BASE_URL,
    CATEGORY_DIRECTORY_URL,
    STAGE_2_GUIDE_URL,
    VMP_PORTAL_URL,
    CACHE_TTL_SECONDS,
    query_live_guide_rag
)

from ui_components import render_purple_segmented_stepper

PAGE_SIZE = 6

def format_web_url(url: str) -> str:
    """Converts raw markdown URLs into clean browser-facing website links by stripping .md."""
    if not url:
        return ""
    if url.endswith(".md"):
        return url[:-3]
    return url

def render_compliance_badge(current_val: str | None, compliant_options: list[str]):
    """Renders a green tick when compliant or amber warning triangle when non-compliant."""
    if not current_val:
        st.markdown(
            "<span style='font-size: 11px; color: #888899;'>⚪ <em>Pending response</em></span>",
            unsafe_allow_html=True
        )
    elif current_val in compliant_options:
        st.markdown(
            """
            <span style='background-color: #eafaf1; color: #1e8449; border: 1px solid #a9dfbf; 
            padding: 3px 9px; border-radius: 6px; font-size: 11.5px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;'>
                ✅ Compliant
            </span>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <span style='background-color: #fef9e7; color: #b7950b; border: 1px solid #f9e79f; 
            padding: 3px 9px; border-radius: 6px; font-size: 11.5px; font-weight: 700; display: inline-flex; align-items: center; gap: 4px;'>
                ⚠️ Non-compliant / Potential Gap
            </span>
            """,
            unsafe_allow_html=True
        )

BASELINE_PREREQUISITES_SCHEMA = {
    "corporate": [
        {
            "key": "incorporated",
            "label": "Company incorporated in Singapore",
            "question": "Is your company incorporated in Singapore?",
            "options": ["Yes", "No"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "operation",
            "label": "Operation for at least 18 months",
            "question": "Has your company been in operation for at least 18 months?",
            "options": ["Yes", "No"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "financial",
            "label": "Financial stability (positive equity & ratio >= 1)",
            "question": "Is your company financially stable (positive net equity, current ratio >= 1)?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "track_record",
            "label": "Government agency track record",
            "question": "Does your company have satisfactory track record with government agencies?",
            "options": ["Yes", "No", "Not currently, but development is underway"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "resources",
            "label": "Sufficient quality resources",
            "question": "Does your company have sufficient quality resources?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "cooling",
            "label": "Free from 1-year IMDA cooling period",
            "question": "Is your company free from any IMDA one-year cooling period?",
            "options": ["Yes", "No"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "invoice_now",
            "label": "InvoiceNow registered account",
            "question": "Has your company signed up for an InvoiceNow account?",
            "options": ["Yes", "No", "Not currently, but development is underway"],
            "compliant_values": ["Yes"]
        }
    ],
    "deployment": [
        {
            "key": "industries",
            "label": "Industry specialization",
            "question": "Select the statement that best describes the industries your solution caters to.",
            "options": ["Many industries", "One or few industries", "Not sure"],
            "compliant_values": ["Many industries", "One or few industries"]
        },
        {
            "key": "customer_track",
            "label": "Deployed with >= 5 SG SMEs for >= 6 months",
            "question": "Has your solution been deployed with at least 5 Singapore-registered SMEs for at least 6 months?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        }
    ],
    "solution": [
        {
            "key": "pricing",
            "label": "Priced reasonably for SMEs",
            "question": "Is your solution priced reasonably for SMEs?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "suitability",
            "label": "Designed for SME needs",
            "question": "Is your solution designed to suit the needs and demands of SMEs?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "productivity",
            "label": "Improves SME productivity",
            "question": "Does your solution help SMEs improve productivity?",
            "options": ["Yes", "No", "Not sure"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "website",
            "label": "Active website showcasing solution",
            "question": "Do you have a website that showcases the solution?",
            "options": ["Yes", "No", "Not currently, but development is underway"],
            "compliant_values": ["Yes"]
        },
        {
            "key": "dapdp",
            "label": "Data protection & analytics compliance",
            "question": "Have you validated compliance with Data Analytics and Personal Data Protection requirements?",
            "options": ["Yes", "No", "Not currently, but development is underway"],
            "compliant_values": ["Yes"]
        }
    ]
}

def sanitize_and_check_injection(user_input: str) -> tuple[bool, str]:
    if not user_input or not user_input.strip():
        return False, "Input cannot be empty."

    jailbreak_patterns = [
        r"ignore (all )?(previous|prior) (instructions|directions|rules)",
        r"system prompt",
        r"reveal (your )?(instructions|secret|api key|prompt)",
        r"bypass (guardrail|filter|policy|restrictions)",
        r"you are now (an unrestricted|a new|dan)",
        r"<script>",
        r"javascript:",
        r"drop table",
    ]

    for pattern in jailbreak_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False, "Input flagged by safety guardrails: contains unauthorized command sequences."

    sanitized = user_input.replace("<", "&lt;").replace(">", "&gt;")
    return True, sanitized

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def fetch_text(url: str) -> str:
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return ""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception:
        return ""

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_category_catalogue():
    markdown = fetch_text(CATEGORY_DIRECTORY_URL)
    if not markdown:
        return {}

    categories = {}
    current_sector = "General"
    lines = markdown.splitlines()

    for line in lines:
        sector_match = re.search(r"Sector:\s*([^*]+)", line, flags=re.IGNORECASE)
        if sector_match:
            current_sector = sector_match.group(1).strip()

        match = re.search(r"\[([^\]]+)\]\(([^)]+\.md)\)", line)
        if not match:
            continue

        category_name = match.group(1).strip()
        relative_url = match.group(2).strip()

        if "/identify-suitable-solution-category/" not in relative_url:
            continue

        category_url = urljoin(CATEGORY_DIRECTORY_URL, relative_url)
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

def resolve_category_info(selected_category_name: str, fallback_url: str = None) -> dict:
    catalogue = get_category_catalogue()
    
    if selected_category_name in catalogue:
        return catalogue[selected_category_name]
    
    if selected_category_name:
        target_lower = selected_category_name.lower().strip()
        for k, v in catalogue.items():
            if k.lower().strip() == target_lower or target_lower in k.lower():
                return v

    if fallback_url and fallback_url.startswith("http"):
        for v in catalogue.values():
            if v["url"].strip() == fallback_url.strip():
                return v

    return {
        "sector": "Identified Solution",
        "category": selected_category_name or "Official Category",
        "url": fallback_url if (fallback_url and fallback_url.startswith("http")) else CATEGORY_DIRECTORY_URL,
        "description": "Multi-functional system that streamlines operations and administration."
    }

@st.cache_data(ttl=CACHE_TTL_SECONDS)
def get_category_requirements(category_url: str):
    if not category_url or not (category_url.startswith("http://") or category_url.startswith("https://")):
        return []

    markdown = fetch_text(category_url)
    if not markdown:
        return []

    questions = []
    lines = markdown.splitlines()
    total_lines = len(lines)

    for i, line in enumerate(lines):
        line_clean = line.strip()
        q_match = re.match(r"#{2,4}\s+Q(\d+)\s*(.*)", line_clean)
        if not q_match:
            continue

        q_number = q_match.group(1)
        heading = q_match.group(2).strip()
        is_mandatory = "preferred" not in heading.lower()
        heading_clean = heading.replace("**", "").replace("*", "").strip()

        question_text = ""
        for next_line in lines[i + 1:min(i + 40, total_lines)]:
            stripped = next_line.strip()
            if re.match(r"#{2,4}\s+Q\d+", stripped):
                break

            if "Main Question:" in stripped:
                question_text = stripped.split("Main Question:", 1)[1].strip()
                break
            elif "Question:" in stripped and not question_text:
                question_text = stripped.split("Question:", 1)[1].strip()
            elif stripped and not question_text and not stripped.startswith("#"):
                if not any(stripped.startswith(prefix) for prefix in ["|", "```", "<!--", "!"]):
                    question_text = stripped

        if not question_text:
            question_text = heading_clean if heading_clean else f"Requirement details for Q{q_number}"

        question_text = question_text.replace("**", "").strip()
        if question_text.endswith(":"):
            question_text = question_text[:-1]

        questions.append({
            "number": q_number,
            "heading": heading_clean,
            "question": question_text,
            "mandatory": is_mandatory
        })

    return questions

def get_gemini_client():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        return None
    return genai.Client(api_key=api_key)

def recommend_categories(vendor_description: str):
    client = get_gemini_client()
    if client is None:
        return {"error": "GEMINI_API_KEY is not configured in Secrets."}

    catalogue = get_category_catalogue()
    catalogue_text = "\n\n".join(
        [
            f"OFFICIAL CATEGORY: {key}\nDESCRIPTION: {val['description']}\nURL: {val['url']}"
            for key, val in catalogue.items()
        ]
    )

    system_instruction = """
You are an IMDA Pre-Approval solution-category recommendation assistant.
Identify relevant official categories from the IMDA catalogue.
Return up to 3 matches.

OUTPUT FORMAT STRICTLY:
MATCH
CATEGORY: <exact official category>
WHY: <one or two sentence explanation>
"""
    user_prompt = f"<official_catalogue>\n{catalogue_text}\n</official_catalogue>\n<vendor_description>\n{vendor_description}\n</vendor_description>"

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=user_prompt,
                config=types.GenerateContentConfig(system_instruction=system_instruction, temperature=0.1)
            )
            return {"answer": response.text, "catalogue": catalogue}
        except Exception as e:
            if "503" in str(e) and attempt < 2:
                time.sleep(2 * (attempt + 1))
                continue
            return {"error": str(e)}

def parse_category_matches(answer: str, catalogue: dict):
    results = []
    blocks = answer.split("MATCH")

    for block in blocks:
        category_match = re.search(r"CATEGORY:\s*(.+)", block)
        why_match = re.search(r"WHY:\s*(.+)", block, flags=re.DOTALL)
        if not category_match:
            continue

        category_text = category_match.group(1).strip()
        matched_key = None

        for key in catalogue:
            if category_text.lower() == key.lower() or key.lower() in category_text.lower():
                matched_key = key
                break

        if matched_key is None:
            continue

        why = why_match.group(1).strip() if why_match else "Relevant based on provided functions."
        why = why.split("MATCH")[0].strip()

        results.append({
            "category_key": matched_key,
            "why": why,
            "url": catalogue[matched_key]["url"]
        })

    return results[:3]

def render_manual_catalogue_browser(key_prefix: str = "manual"):
    try:
        catalogue = get_category_catalogue()
        if not catalogue:
            st.info("Category catalogue is currently loading...")
            return

        sectors = sorted(list(set([val["sector"] for val in catalogue.values()])))
        selected_sector = st.radio(
            "Filter by Sector",
            ["All Sectors"] + sectors,
            horizontal=True,
            key=f"{key_prefix}_sector_filter"
        )
        search_query = st.text_input(
            "Search categories by keyword",
            placeholder="e.g. Cybersecurity, Invoicing, POS...",
            key=f"{key_prefix}_cat_search"
        )

        filtered_items = []
        for k, v in catalogue.items():
            if selected_sector != "All Sectors" and v["sector"] != selected_sector:
                continue
            if search_query.strip() and (
                search_query.lower() not in k.lower()
                and search_query.lower() not in v["description"].lower()
            ):
                continue
            filtered_items.append((k, v))

        total_items = len(filtered_items)
        if total_items == 0:
            st.warning("No matching categories found for your search criteria.")
            return

        total_pages = max(1, (total_items + PAGE_SIZE - 1) // PAGE_SIZE)
        page_key = f"{key_prefix}_catalog_page"
        if page_key not in st.session_state:
            st.session_state[page_key] = 1
        if st.session_state[page_key] > total_pages:
            st.session_state[page_key] = total_pages

        st.caption(f"Showing {total_items} categories (Page {st.session_state[page_key]} of {total_pages})")

        start_idx = (st.session_state[page_key] - 1) * PAGE_SIZE
        end_idx = min(start_idx + PAGE_SIZE, total_items)
        page_items = filtered_items[start_idx:end_idx]

        for i in range(0, len(page_items), 2):
            col1, col2 = st.columns(2)
            with col1:
                if i < len(page_items):
                    k1, v1 = page_items[i]
                    with st.container(border=True):
                        st.markdown(f"<span style='background:#f7eaf3; color:#7a1d5a; padding:1px 6px; border-radius:4px; font-size:10px; font-weight:700;'>{v1['sector']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<h6 style='font-size: 14px; font-weight: 700; color: #2b0b2e; margin-top: 6px;'>{v1['category']}</h6>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 12px; color: #636375; line-height: 1.4;'>{v1['description'] or 'Official IMDA pre-approved solution category.'}</p>", unsafe_allow_html=True)
                        if st.button("Select Category →", key=f"{key_prefix}_btn_{start_idx + i}", use_container_width=True):
                            st.session_state.selected_category = k1
                            st.session_state.selected_category_url = v1["url"]
                            st.session_state.assessment_step = 1
                            st.rerun()

            with col2:
                if i + 1 < len(page_items):
                    k2, v2 = page_items[i + 1]
                    with st.container(border=True):
                        st.markdown(f"<span style='background:#f7eaf3; color:#7a1d5a; padding:1px 6px; border-radius:4px; font-size:10px; font-weight:700;'>{v2['sector']}</span>", unsafe_allow_html=True)
                        st.markdown(f"<h6 style='font-size: 14px; font-weight: 700; color: #2b0b2e; margin-top: 6px;'>{v2['category']}</h6>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 12px; color: #636375; line-height: 1.4;'>{v2['description'] or 'Official IMDA pre-approved solution category.'}</p>", unsafe_allow_html=True)
                        if st.button("Select Category →", key=f"{key_prefix}_btn_{start_idx + i + 1}", use_container_width=True):
                            st.session_state.selected_category = k2
                            st.session_state.selected_category_url = v2["url"]
                            st.session_state.assessment_step = 1
                            st.rerun()

        if total_pages > 1:
            st.markdown("---")
            page_cols = st.columns(min(total_pages, 10))
            for p_num in range(1, total_pages + 1):
                col_idx = (p_num - 1) % 10
                with page_cols[col_idx]:
                    btn_type = "primary" if p_num == st.session_state[page_key] else "secondary"
                    if st.button(str(p_num), key=f"{key_prefix}_page_{p_num}", type=btn_type, use_container_width=True):
                        st.session_state[page_key] = p_num
                        st.rerun()
    except Exception as e:
        st.error(f"Error loading directory: {e}")

def populate_test_sample_data():
    """Dynamically sets every requirement in the category checklist and baseline schema to compliant."""
    target_category_key = "Early Childhood: Pre-School Management System"
    catalogue = get_category_catalogue()
    target_url = catalogue.get(target_category_key, {}).get("url", CATEGORY_DIRECTORY_URL)

    st.session_state.selected_category = target_category_key
    st.session_state.selected_category_url = target_url

    reqs = get_category_requirements(target_url)
    answers = {}
    if reqs:
        for q in reqs:
            if q.get("mandatory", True):
                answers[str(q["number"])] = "Yes"
    else:
        for i in range(1, 25):
            answers[str(i)] = "Yes"
    
    st.session_state.category_answers = answers

    schema_answers = {}
    for section_items in BASELINE_PREREQUISITES_SCHEMA.values():
        for item in section_items:
            schema_answers[item["key"]] = item["compliant_values"][0]

    st.session_state.assessment = schema_answers

    st.session_state.sub_company = "Alpha Digital Singapore Pte Ltd"
    st.session_state.sub_person = "Alex Tan"
    st.session_state.sub_email = "alex.tan@alphadigital.sg"
    st.session_state.sub_phone = "+65 9123 4567"
    st.session_state.sub_inquiry = "We meet all baseline requirements and category checklists, ready for Stage 2 submission."

def clear_all_assessment_data():
    """Resets all assessment questions, answers, and contact inputs to completely blank."""
    st.session_state.assessment = {}
    st.session_state.category_answers = {}
    st.session_state.sub_company = ""
    st.session_state.sub_person = ""
    st.session_state.sub_email = ""
    st.session_state.sub_phone = ""
    st.session_state.sub_inquiry = ""
    st.session_state.selected_category = None
    st.session_state.selected_category_url = None
    st.session_state.form_submitted = False
    st.session_state.assessment_step = 0
    st.session_state.target_focus_key = None

def render_step_1_discovery():
    st.markdown("### 🔍 Step 1: Solution Category Discovery & Feasibility Pre-Check")
    st.caption("Verify whether your product matches an official IMDA pre-approved category before starting self-assessment.")

    current_desc = st.session_state.assessment.get("solution_description", "")
    if st.session_state.get("auto_trigger_search", False) and current_desc.strip():
        st.session_state.auto_trigger_search = False
        is_safe, sanitized_text = sanitize_and_check_injection(current_desc)
        if is_safe:
            with st.spinner("Analyzing against official IMDA categories..."):
                result = recommend_categories(sanitized_text)
            if "error" not in result:
                st.session_state.category_suggestions = parse_category_matches(result["answer"], result["catalogue"])

    tab_ai, tab_manual = st.tabs(["🤖 AI Semantic Matcher", "📂 Manual Directory Browser"])

    with tab_ai:
        with st.container(border=True):
            description = st.text_area(
                "Describe your solution capabilities",
                height=100,
                value=st.session_state.assessment.get("solution_description", ""),
                placeholder='e.g., "My solution provides endpoint anti-malware, firewall protection, and automated threat detection for SME laptops."'
            )
            st.session_state.assessment["solution_description"] = description

            if st.button("Find Matching Categories via AI →", type="primary", use_container_width=True):
                is_safe, sanitized_text = sanitize_and_check_injection(description)
                if not is_safe:
                    st.error(sanitized_text)
                else:
                    with st.spinner("Analyzing against official IMDA categories..."):
                        result = recommend_categories(sanitized_text)

                    if "error" in result:
                        st.error(result["error"])
                    else:
                        matches = parse_category_matches(result["answer"], result["catalogue"])
                        st.session_state.category_suggestions = matches

        if st.session_state.category_suggestions:
            st.markdown("---")
            st.markdown(
                "<h5 style='font-size: 16px; font-weight: 700; color: #581845;'>💡 AI Recommended Matches</h5>",
                unsafe_allow_html=True
            )
            for index, suggestion in enumerate(st.session_state.category_suggestions):
                category_key = suggestion["category_key"]
                catalogue = get_category_catalogue()
                category = catalogue.get(category_key, {"url": CATEGORY_DIRECTORY_URL, "description": ""})

                with st.container(border=True):
                    st.markdown(
                        f"<h6 style='font-size: 15px; font-weight: 700; color: #2b0b2e;'>{index + 1}. {category_key}</h6>",
                        unsafe_allow_html=True
                    )
                    st.markdown(
                        f"<p style='font-size: 12.5px; color: #555566;'>{suggestion['why']}</p>",
                        unsafe_allow_html=True
                    )
                    if st.button(
                        "Confirm & Proceed to Category Functional Checklist →",
                        key=f"select_ai_cat_{index}",
                        use_container_width=True
                    ):
                        st.session_state.selected_category = category_key
                        st.session_state.selected_category_url = category["url"]
                        st.session_state.assessment_step = 1
                        st.rerun()

            st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
            with st.container(border=True):
                st.markdown(
                    """
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 18px;">📂</span>
                        <strong style="font-size: 14.5px; color: #2b0b2e;">Don't see a suitable match?</strong>
                    </div>
                    <p style="font-size: 12.5px; color: #636375; margin: 4px 0 12px 0;">
                        If your solution does not align with the AI suggestions above, browse the complete 
                        catalogue manually by sector or keyword search below.
                    </p>
                    """,
                    unsafe_allow_html=True
                )
                with st.expander("📂 Browse Full IMDA Category Directory Manually", expanded=False):
                    render_manual_catalogue_browser(key_prefix="ai_tab_fallback")

    with tab_manual:
        render_manual_catalogue_browser(key_prefix="manual_tab")

def render_step_2_checklist():
    st.markdown("### 📋 Step 2: Category Functional Checklist")
    selected = st.session_state.get("selected_category")
    stored_url = st.session_state.get("selected_category_url")

    if not selected:
        with st.container(border=True):
            st.warning("⚠️ No solution category has been selected yet.")
            st.write("Please complete Step 1 to discover or select your category first.")
            if st.button("← Go to Step 1: Category Discovery", type="primary"):
                st.session_state.assessment_step = 0
                st.rerun()
        return

    category = resolve_category_info(selected, stored_url)
    resolved_url = category.get("url") or CATEGORY_DIRECTORY_URL

    with st.container(border=True):
        st.success(f"Target Category: **{selected}**")
        st.write(category.get("description", "Multi-functional system that streamlines operations and administration."))
        if resolved_url and resolved_url.startswith("http"):
            clean_web_link = format_web_url(resolved_url)
            st.link_button("Open official IMDA requirements page ↗", clean_web_link)

    st.markdown("---")
    st.subheader("1. Mandatory Functional Checklist")
    st.caption("Indicate your solution's compliance for each requirement. Real-time compliance badges indicate eligibility.")

    with st.spinner("Loading official checklist..."):
        requirements = get_category_requirements(resolved_url)

    mandatory = [q for q in requirements if q["mandatory"]]
    preferred = [q for q in requirements if not q["mandatory"]]

    target_focus = st.session_state.get("target_focus_key")

    if not mandatory:
        st.info("No explicit checklist questions were found for this category. You may verify details on the official IMDA page above and proceed to prerequisite validation.")
    else:
        for question in mandatory:
            q_num = str(question['number'])
            key = f"category_q_{q_num}"
            existing_ans = st.session_state.category_answers.get(q_num)
            ans_opts = ["Yes", "No", "Not sure"]
            ans_idx = ans_opts.index(existing_ans) if existing_ans in ans_opts else None

            is_focused = (target_focus == f"cat_q_{q_num}")

            st.markdown(f'<div id="anchor_cat_q_{q_num}"></div>', unsafe_allow_html=True)

            with st.container(border=True):
                if is_focused:
                    st.markdown(
                        """
                        <div style='background-color: #fff0f0; border-left: 4px solid #d8232a; padding: 6px 10px; margin-bottom: 8px; border-radius: 4px;'>
                            <strong style='color: #d8232a; font-size: 12px;'>👉 Focus: Please update this requirement</strong>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                q_col1, q_col2 = st.columns([5.2, 1.8])
                with q_col1:
                    st.markdown(f"**Q{question['number']}** — {question['question']}")
                with q_col2:
                    render_compliance_badge(existing_ans, compliant_options=["Yes"])

                chosen_q = st.radio(
                    f"Select compliance status for Q{question['number']}",
                    ans_opts,
                    index=ans_idx,
                    key=key,
                    label_visibility="collapsed"
                )
                if chosen_q is not None and chosen_q != existing_ans:
                    st.session_state.category_answers[q_num] = chosen_q
                    st.session_state.target_focus_key = None
                    st.rerun()

        if target_focus and target_focus.startswith("cat_q_"):
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

        if preferred:
            with st.expander(f"View {len(preferred)} Preferred Requirements"):
                for question in preferred:
                    with st.container(border=True):
                        st.write(f"**Q{question['number']}** — {question['question']}")

    st.markdown("")
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button("← Back to Step 1: Category Discovery", use_container_width=True):
            st.session_state.assessment_step = 0
            st.session_state.target_focus_key = None
            st.rerun()
    with col_b2:
        if st.button("Proceed to Step 3: Prerequisite Validation →", type="primary", use_container_width=True):
            st.session_state.assessment_step = 2
            st.session_state.target_focus_key = None
            st.rerun()

def render_step_3_prerequisites():
    st.markdown("### 🏢 Step 3: Baseline Prerequisite Validation")
    st.caption("Confirm foundational corporate, financial, and deployment prerequisites with real-time feedback.")

    if st.session_state.get("selected_category"):
        st.info(f"Target Category: **{st.session_state.selected_category}**")

    tab_names = ["1. Corporate & Financials", "2. SME Deployment Track Record", "3. Solution Suitability"]
    current_tab_idx = st.session_state.get("prereq_tab_idx", 0)

    selected_tab_name = st.radio(
        "Section",
        tab_names,
        index=current_tab_idx,
        horizontal=True,
        key="prereq_subtab_radio",
        label_visibility="collapsed"
    )
    st.session_state.prereq_tab_idx = tab_names.index(selected_tab_name)
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

    target_focus = st.session_state.get("target_focus_key")

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

def render_step_4_review_and_submit():
    st.markdown("### 📊 Step 4: Readiness Review, Gap Audit & Submission Summary")
    selected = st.session_state.get("selected_category", "Not selected")

    front_gaps = []
    for section_name, section_items in BASELINE_PREREQUISITES_SCHEMA.items():
        tab_idx_map = {"corporate": 0, "deployment": 1, "solution": 2}
        for item in section_items:
            k = item["key"]
            val = st.session_state.assessment.get(k)
            if k == "customer_track" and st.session_state.assessment.get("industries") != "One or few industries":
                continue
            if val and val not in item["compliant_values"]:
                front_gaps.append({"key": k, "item": item["label"], "status": val, "tab_idx": tab_idx_map[section_name]})
            elif not val:
                front_gaps.append({"key": k, "item": item["label"], "status": "Unanswered", "tab_idx": tab_idx_map[section_name]})

    unmet_cat_questions = []
    for q_num, ans in st.session_state.category_answers.items():
        if ans in ["No", "Not sure"]:
            unmet_cat_questions.append({"number": q_num, "status": ans})

    total_gaps_count = len(front_gaps) + len(unmet_cat_questions)

    with st.container(border=True):
        if total_gaps_count > 0:
            st.warning(f"⚠️ System detected **{total_gaps_count}** requirement gap(s) across your assessment:")
            
            if unmet_cat_questions:
                st.markdown(f"**Category Functional Checklist Gaps for {selected}:**")
                for uq in unmet_cat_questions:
                    gap_c1, gap_c2 = st.columns([5.2, 1.3])
                    with gap_c1:
                        st.markdown(f"- ⚠️ **Q{uq['number']} ({uq['status']})**")
                    with gap_c2:
                        if st.button("Edit ✏️", key=f"edit_cat_q_{uq['number']}", use_container_width=True):
                            st.session_state.assessment_step = 1
                            st.session_state.target_focus_key = f"cat_q_{uq['number']}"
                            st.rerun()

            if front_gaps:
                st.markdown("**Baseline Prerequisite Gaps:**")
                for fg_idx, fg in enumerate(front_gaps):
                    gap_col1, gap_col2 = st.columns([5.2, 1.3])
                    with gap_col1:
                        st.markdown(f"- 🔴 **{fg['item']}** (Status: *{fg['status']}*)")
                    with gap_col2:
                        if st.button("Edit ✏️", key=f"edit_gap_{fg_idx}", use_container_width=True):
                            st.session_state.assessment_step = 2
                            st.session_state.prereq_tab_idx = fg["tab_idx"]
                            st.session_state.target_focus_key = f"prereq_{fg['key']}"
                            st.rerun()
        else:
            st.success("✅ **Full Compliance:** Your solution meets all evaluated baseline prerequisites and category functional requirements!")

    st.markdown("---")

    st.subheader("Vendor Contact Details & Pre-Submission Inquiry")
    with st.container(border=True):
        with st.form("vendor_submission_form"):
            col_c1, col_c2 = st.columns(2)
            with col_c1:
                company_name = st.text_input("Company Registered Name *", value=st.session_state.get("sub_company", ""), placeholder="e.g. Acme Tech Solutions Pte Ltd")
                contact_person = st.text_input("Contact Person Name *", value=st.session_state.get("sub_person", ""), placeholder="e.g. John Tan")
            with col_c2:
                contact_email = st.text_input("Corporate Email Address *", value=st.session_state.get("sub_email", ""), placeholder="e.g. john.tan@acme.com")
                contact_phone = st.text_input("Contact Number *", value=st.session_state.get("sub_phone", ""), placeholder="e.g. +65 9123 4567")

            vendor_inquiry = st.text_area(
                "Inquiry / Clarification Notes",
                value=st.session_state.get("sub_inquiry", ""),
                placeholder="Optional: Enter any questions regarding timeline or alternative compliance pathways for IMDA officers.",
                height=90
            )

            submit_button = st.form_submit_button("Submit Assessment & Generate Summary →", type="primary", use_container_width=True)

    if submit_button:
        if not company_name or not contact_person or not contact_email:
            st.error("Please fill in all mandatory contact fields (Company Name, Contact Person, and Email).")
            st.session_state.form_submitted = False
        else:
            st.session_state.form_submitted = True
            st.session_state.sub_company = company_name
            st.session_state.sub_person = contact_person
            st.session_state.sub_email = contact_email
            st.session_state.sub_phone = contact_phone
            st.session_state.sub_inquiry = vendor_inquiry

    if st.session_state.get("form_submitted", False):
        st.success("🎉 Assessment Summary Generated Successfully!")

        with st.container(border=True):
            st.markdown("### 📋 Submission Summary")
            st.markdown(f"**Target Category:** {selected}")
            st.markdown(f"**Company:** {st.session_state.sub_company} | **Contact:** {st.session_state.sub_person} ({st.session_state.sub_email}, {st.session_state.sub_phone})")

            if total_gaps_count > 0:
                st.markdown("#### Detected Gaps for Review:")
                for uq in unmet_cat_questions:
                    st.markdown(f"- Category Requirement Q{uq['number']} ({uq['status']})")
                for fg in front_gaps:
                    st.markdown(f"- Baseline Prerequisite: {fg['item']} ({fg['status']})")
            else:
                st.markdown("✅ **Readiness Status:** 100% compliant across evaluated criteria.")

            if st.session_state.sub_inquiry.strip():
                st.markdown("#### Inquiries / Notes:")
                st.write(st.session_state.sub_inquiry)

        officer_email = st.secrets.get("OFFICER_REVIEW_EMAIL", "seah_jie_ling@imda.gov.sg")
        st.info(f"📧 **Officer Routing:** Record prepared for dispatch to **`{officer_email}`**.")
        st.warning("ℹ️ **Prototype Notice:** Live SMTP servers are not configured for this prototype session; emails will not be transmitted externally.")

        st.markdown("---")

        if total_gaps_count > 0:
            with st.container(border=True):
                st.markdown("### 🤖 Recommended Next Steps: Address Your Identified Gaps")
                st.write(
                    "Your assessment flagged requirement gaps. You can pass these items directly to "
                    "the AI Copilot to get actionable remediation steps and alternative compliance pathways."
                )
                if st.button("💬 Consult AI Copilot for Remediation Advice →", type="primary", use_container_width=True):
                    gap_lines = [f"- Category Requirement Q{uq['number']} ({uq['status']})" for uq in unmet_cat_questions]
                    gap_lines += [f"- Baseline Prerequisite: {fg['item']} ({fg['status']})" for fg in front_gaps]
                    gaps_text = "\n".join(gap_lines)

                    auto_prompt = (
                        f"I have completed my self-assessment for the pre-approval category '{selected}'. "
                        f"The system flagged the following requirement gaps:\n\n{gaps_text}\n\n"
                        "Based on the official IMDA Pre-Approval Guide, what specific remediation steps, "
                        "alternative compliance pathways, or documentation can I prepare to address these gaps?"
                    )
                    st.session_state.chat_messages.append({"role": "user", "content": auto_prompt})

                    client = get_gemini_client()
                    if client:
                        with st.spinner("Analyzing gaps against official IMDA guide..."):
                            auto_response = query_live_guide_rag(
                                client,
                                user_query=auto_prompt,
                                chat_history=st.session_state.chat_messages,
                                user_assessment=st.session_state.assessment,
                                selected_category=st.session_state.selected_category,
                                model_name=MODEL_NAME
                            )
                        st.session_state.chat_messages.append({"role": "assistant", "content": auto_response})

                    st.session_state.show_chat_dialog = True
                    st.rerun()

        else:
            with st.container(border=True):
                st.markdown("### 🚀 Next Steps: Prepare for Stage 2 Application & VMP Submission")
                st.write(
                    "Your solution meets all evaluated baseline criteria and category functional requirements! "
                    "Follow the official **Stage 2: Vendor Application** guide to prepare your solution deck, "
                    "pricing matrix, and customer proof before submitting through the **Vendor Management Portal (VMP)**."
                )
                col_d1, col_d2 = st.columns(2)
                with col_d1:
                    st.link_button(
                        "📖 Read Stage 2 Guide ↗",
                        STAGE_2_GUIDE_URL,
                        use_container_width=True
                    )
                with col_d2:
                    st.link_button(
                        "🏛️ Launch VMP Portal ↗",
                        VMP_PORTAL_URL,
                        use_container_width=True
                    )

    st.markdown("")
    if st.button("← Back to Step 3: Prerequisite Validation", use_container_width=True):
        st.session_state.assessment_step = 2
        st.session_state.target_focus_key = None
        st.rerun()

def render_pre_approval_assessment():
    with st.container():
        ctrl_col1, ctrl_col2, _ = st.columns([2.2, 1.8, 3.5])
        with ctrl_col1:
            if st.button("⚡ Auto-Populate Sample Data (Test Mode)", key="btn_test_populate", use_container_width=True):
                populate_test_sample_data()
                st.success("Test data populated! Category selected, checklist & prerequisites compliant.")
                st.rerun()
        with ctrl_col2:
            if st.button("🗑️ Clear All Answers", key="btn_test_clear", use_container_width=True):
                clear_all_assessment_data()
                st.info("Assessment cleared. All questions reset to unanswered.")
                st.rerun()

    st.markdown("<div style='margin-bottom: 8px;'></div>", unsafe_allow_html=True)

    render_purple_segmented_stepper(st.session_state.assessment_step)

    if st.session_state.assessment_step == 0:
        render_step_1_discovery()
    elif st.session_state.assessment_step == 1:
        render_step_2_checklist()
    elif st.session_state.assessment_step == 2:
        render_step_3_prerequisites()
    elif st.session_state.assessment_step == 3:
        render_step_4_review_and_submit()
