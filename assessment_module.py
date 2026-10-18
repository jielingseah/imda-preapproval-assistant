"""Assessment Module UI Orchestrator for IMDA Pre-Approval Assistant.

Focuses strictly on Streamlit presentation and user interaction for Steps 1
through 4.
Zero CSS styling defined locally — all visual styles are read from
ui_components.py.
"""

from datetime import datetime
import streamlit as st

# Centralized constants and RAG
from imda_knowledge import (
    CATEGORY_DIRECTORY_URL,
    MODEL_NAME,
    query_live_guide_rag,
    STAGE_2_GUIDE_URL,
    VMP_PORTAL_URL,
)

# Assessment Data Schemas & Backend Services
from assessment_schemas import BASELINE_PREREQUISITES_SCHEMA
from assessment_service import (
    format_web_url,
    get_category_catalogue,
    get_category_requirements,
    get_gemini_client,
    parse_category_matches,
    recommend_categories,
    resolve_category_info,
    sanitize_and_check_injection,
)

# Unified UI components
from ui_components import render_purple_segmented_stepper

PAGE_SIZE = 6
UNLISTED_CAT_LABEL = "Unlisted / New Category Inquiry"


def get_default_inquiry_text(selected_cat: str, has_gaps: bool) -> str:
  """Returns a context-accurate default inquiry note based on vendor assessment outcome."""
  if selected_cat == UNLISTED_CAT_LABEL:
    return (
        "We understand our solution falls under an unlisted category. "
        "We are submitting our company profile, product website, and solution"
        " capabilities as an Expression of Interest for IMDA's future roadmap"
        " and category review cycles."
    )
  elif has_gaps:
    return (
        "We are currently reviewing our identified prerequisite/checklist gaps"
        " and would like to seek clarification on acceptable remediation"
        " documentation and alternative compliance pathways."
    )
  else:
    return (
        "We meet all baseline requirements and category checklists, ready for"
        " Stage 2 submission."
    )


def render_compliance_badge(
    current_val: str | None, compliant_options: list[str]
):
  """Renders compliance status using centralized CSS classes from ui_components."""
  if not current_val:
    st.markdown(
        "<span class='compliance-pill-pending'>⚪ <em>Pending"
        " response</em></span>",
        unsafe_allow_html=True,
    )
  elif current_val in compliant_options:
    st.markdown(
        "<span class='compliance-pill-compliant'>✅ Compliant</span>",
        unsafe_allow_html=True,
    )
  else:
    st.markdown(
        "<span class='compliance-pill-gap'>⚠️ Non-compliant / Potential"
        " Gap</span>",
        unsafe_allow_html=True,
    )


def populate_test_sample_data():
  """Dynamically populates compliant answers for testing."""
  target_category_key = "Early Childhood: Pre-School Management System"
  catalogue = get_category_catalogue()
  target_url = catalogue.get(target_category_key, {}).get(
      "url", CATEGORY_DIRECTORY_URL
  )

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
  st.session_state.assessment["solution_description"] = (
      "Comprehensive cloud platform for pre-school administrative automation,"
      " attendance tracking, and fee collection."
  )
  st.session_state.sub_company = "Alpha Digital Singapore Pte Ltd"
  st.session_state.sub_website = "https://www.alphadigital.sg"
  st.session_state.sub_person = "Alex Tan"
  st.session_state.sub_email = "alex.tan@alphadigital.sg"
  st.session_state.sub_phone = "+65 9123 4567"
  st.session_state.sub_inquiry = get_default_inquiry_text(
      target_category_key, has_gaps=False
  )


def clear_all_assessment_data():
  """Resets all assessment questions, answers, and contact inputs to completely blank."""
  st.session_state.assessment = {}
  st.session_state.category_answers = {}
  st.session_state.sub_company = ""
  st.session_state.sub_website = ""
  st.session_state.sub_person = ""
  st.session_state.sub_email = ""
  st.session_state.sub_phone = ""
  st.session_state.sub_inquiry = ""
  st.session_state.selected_category = None
  st.session_state.selected_category_url = None
  st.session_state.form_submitted = False
  st.session_state.assessment_step = 0
  st.session_state.target_focus_key = None
  st.session_state.prereq_tab_idx = 0


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
        key=f"{key_prefix}_sector_filter",
    )
    search_query = st.text_input(
        "Search categories by keyword",
        placeholder="e.g. Cybersecurity, Invoicing, POS...",
        key=f"{key_prefix}_cat_search",
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
      if st.button(
          "Proceed with 'Unlisted / New Category' →",
          key=f"{key_prefix}_unlisted_fallback",
          type="primary",
      ):
        st.session_state.selected_category = UNLISTED_CAT_LABEL
        st.session_state.selected_category_url = None
        st.session_state.assessment_step = 1
        st.rerun()
      return

    total_pages = max(1, (total_items + PAGE_SIZE - 1) // PAGE_SIZE)
    page_key = f"{key_prefix}_catalog_page"
    if page_key not in st.session_state:
      st.session_state[page_key] = 1
    if st.session_state[page_key] > total_pages:
      st.session_state[page_key] = total_pages

    st.caption(
        f"Showing {total_items} categories (Page"
        f" {st.session_state[page_key]} of {total_pages})"
    )

    start_idx = (st.session_state[page_key] - 1) * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total_items)
    page_items = filtered_items[start_idx:end_idx]

    for i in range(0, len(page_items), 2):
      col1, col2 = st.columns(2)
      with col1:
        if i < len(page_items):
          k1, v1 = page_items[i]
          with st.container(border=True):
            st.markdown(
                f"<span class='portal-card-tag'>{v1['sector']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"<h6>{v1['category']}</h6>", unsafe_allow_html=True)
            st.markdown(
                f"<p>{v1['description'] or 'Official IMDA pre-approved solution category.'}</p>",
                unsafe_allow_html=True,
            )
            if st.button(
                "Select Category →",
                key=f"{key_prefix}_btn_{start_idx + i}",
                type="primary",
                use_container_width=True,
            ):
              st.session_state.selected_category = k1
              st.session_state.selected_category_url = v1["url"]
              st.session_state.assessment_step = 1
              st.rerun()

      with col2:
        if i + 1 < len(page_items):
          k2, v2 = page_items[i + 1]
          with st.container(border=True):
            st.markdown(
                f"<span class='portal-card-tag'>{v2['sector']}</span>",
                unsafe_allow_html=True,
            )
            st.markdown(f"<h6>{v2['category']}</h6>", unsafe_allow_html=True)
            st.markdown(
                f"<p>{v2['description'] or 'Official IMDA pre-approved solution category.'}</p>",
                unsafe_allow_html=True,
            )
            if st.button(
                "Select Category →",
                key=f"{key_prefix}_btn_{start_idx + i + 1}",
                type="primary",
                use_container_width=True,
            ):
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
          btn_type = (
              "primary" if p_num == st.session_state[page_key] else "secondary"
          )
          if st.button(
              str(p_num),
              key=f"{key_prefix}_page_{p_num}",
              type=btn_type,
              use_container_width=True,
          ):
            st.session_state[page_key] = p_num
            st.rerun()
  except Exception as e:
    st.error(f"Error loading directory: {e}")


# =========================================================
# STEP 1: DISCOVERY & FEASIBILITY PRE-CHECK
# =========================================================


def render_step_1_discovery():
  st.markdown(
      "### 🔍 Step 1: Solution Category Discovery & Feasibility Pre-Check"
  )
  st.caption(
      "Verify whether your product matches an official IMDA pre-approved"
      " category before starting self-assessment."
  )

  current_desc = st.session_state.assessment.get("solution_description", "")
  if st.session_state.get("auto_trigger_search", False) and current_desc.strip():
    st.session_state.auto_trigger_search = False
    is_safe, sanitized_text = sanitize_and_check_injection(current_desc)
    if is_
