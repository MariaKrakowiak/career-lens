import uuid

import pandas as pd
import streamlit as st

from config import get_settings
from databricks_client import DatabricksSQL
from extractor import (
    extract_job_candidate,
    validate_result,
)
from matcher import calculate_match
from utils import (
    clean_text,
    extract_pdf_text,
)


st.set_page_config(
    page_title="Career Lens",
    page_icon="🎯",
    layout="wide",
)


# --- Page styling ---

st.markdown(
    """
<style>
:root {
    --primary: #4f46e5;
    --primary-dark: #3730a3;
    --purple: #7c3aed;
    --bg: #f8fafc;
    --surface: #ffffff;
    --text: #0f172a;
    --text-secondary: #475569;
    --text-muted: #94a3b8;
    --border: #e2e8f0;
}

.stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: radial-gradient(circle at top right, rgba(99, 102, 241, 0.08), transparent 30%), var(--bg);
}

.eyebrow {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    background: #eef2ff;
    color: #4f46e5;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.8px;
    margin-bottom: 12px;
}
.hero-title {
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-size: clamp(36px, 5vw, 54px);
    font-weight: 800;
    letter-spacing: -2px;
    margin: 0;
}
.hero-description {
    color: #475569;
    font-size: 17px;
    line-height: 1.7;
    max-width: 650px;
    margin: 16px auto 0;
}

.feature-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 18px;
    padding: 24px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    text-align: center;
}
.feature-icon {
    width: 48px;
    height: 48px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
    font-size: 24px;
    margin: 0 auto 12px;
}
.feature-icon.blue { background: #eef2ff; }
.feature-icon.purple { background: #ede9fe; }
.feature-icon.green { background: #d1fae5; }
.feature-card h3 { margin: 0 0 6px; font-size: 16px; font-weight: 700; color: #0f172a; }
.feature-card p { margin: 0; color: #475569; font-size: 14px; line-height: 1.6; }

.app-footer {
    text-align: center;
    color: #94a3b8;
    font-size: 13px;
    padding: 40px 0 20px;
    border-top: 1px solid #e2e8f0;
    margin-top: 40px;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #4f46e5, #3730a3);
    color: white;
    border: none;
    border-radius: 14px;
    font-weight: 700;
    font-size: 17px;
    padding: 16px 32px;
    box-shadow: 0 6px 20px rgba(79, 70, 229, 0.3);
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button[kind="primary"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(79, 70, 229, 0.4);
}

[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
}
[data-testid="stMetricValue"] {
    color: #4f46e5;
    font-weight: 800;
}

.stApp h2, .stApp h3 {
    color: #0f172a;
    font-weight: 700;
}

/* Score bars */
.score-bar-container {
    background: #f1f5f9;
    border-radius: 999px;
    height: 10px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s ease;
}
.score-bar-fill.green { background: linear-gradient(90deg, #059669, #10b981); }
.score-bar-fill.amber { background: linear-gradient(90deg, #d97706, #f59e0b); }
.score-bar-fill.red { background: linear-gradient(90deg, #dc2626, #ef4444); }

/* Recommendation banner */
.rec-banner {
    border-radius: 14px;
    padding: 18px 24px;
    font-size: 15px;
    font-weight: 600;
    text-align: center;
    margin: 20px 0;
}
.rec-banner.strong { background: #d1fae5; color: #065f46; border: 1px solid #6ee7b7; }
.rec-banner.reasonable { background: #dbeafe; color: #1e40af; border: 1px solid #93c5fd; }
.rec-banner.gaps { background: #fef3c7; color: #92400e; border: 1px solid #fcd34d; }
.rec-banner.low { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}
.stTabs [data-baseweb="tab"] {
    padding: 10px 18px;
    border-radius: 10px;
    background: #ffffff;
    border: 1px solid #e2e8f0;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #4f46e5, #7c3aed) !important;
    color: white !important;
    border: none !important;
}

/* Hero section card */
.hero-section {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 48px 24px;
    margin: 20px 0 40px;
    background: linear-gradient(135deg, rgba(238, 242, 255, 0.6), rgba(237, 233, 254, 0.4));
    border-radius: 24px;
    border: 1px solid rgba(99, 102, 241, 0.08);
}

/* Top accent bar */
.stApp::before {
    content: "";
    display: block;
    height: 4px;
    background: linear-gradient(90deg, #4f46e5, #7c3aed, #4f46e5);
    background-size: 200% 100%;
    animation: shimmer 4s ease-in-out infinite;
}
@keyframes shimmer {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Section step badges */
.step-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background: linear-gradient(135deg, #4f46e5, #7c3aed);
    color: white;
    font-weight: 700;
    font-size: 14px;
    margin-right: 10px;
    vertical-align: middle;
}

/* Dataframe styling */
.stDataFrame {
    border-radius: 12px;
    overflow: hidden;
}

/* Result header */
.result-header {
    text-align: center;
    font-size: 24px;
    font-weight: 800;
    color: #0f172a;
    margin: 20px 0 10px;
}

/* DataFrame container */
[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
}
[data-testid="stDataFrame"] .ag-header {
    background: linear-gradient(135deg, #eef2ff, #ede9fe) !important;
    font-weight: 700;
}
[data-testid="stDataFrame"] .ag-row-even {
    background: #ffffff;
}
[data-testid="stDataFrame"] .ag-row-odd {
    background: #f8fafc;
}
[data-testid="stDataFrame"] .ag-row:hover {
    background: #eef2ff !important;
}

/* Static table */
.stTable table {
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    overflow: hidden;
    width: 100%;
}
.stTable th {
    background: linear-gradient(135deg, #eef2ff, #ede9fe) !important;
    font-weight: 700;
    color: #0f172a !important;
}
.stTable tr:nth-child(even) td {
    background: #f8fafc;
}
.stTable tr:hover td {
    background: #eef2ff;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- Settings (silent) ---

try:

    settings = get_settings()

except Exception as error:

    st.error(
        str(error)
    )

    st.stop()

# --- Hero ---

st.markdown(
    """
<div class="hero-section">
    <div class="eyebrow">✨ AI-POWERED JOB MATCHING</div>
    <h1 class="hero-title">Career Lens</h1>
    <p class="hero-description">
        Provide your CV and a job description — Career Lens will extract requirements,
        identify skill gaps, calculate an explainable match score, and recommend
        whether the application is worth pursuing.
    </p>
</div>
""",
    unsafe_allow_html=True,
)


left_column, right_column = st.columns(
    2
)


with left_column:

    st.markdown(
        '<h3><span class="step-badge">1</span> Job description</h3>',
        unsafe_allow_html=True,
    )

    job_input_method = st.radio(
        "Input method",
        ["Paste text", "Upload PDF"],
        key="job_input_method",
        horizontal=True,
    )

    job_text = ""

    if job_input_method == "Paste text":

        job_text = st.text_area(
            "Paste job description",
            height=400,
            placeholder=(
                "Paste the complete job description here..."
            ),
        )

    else:

        job_file = st.file_uploader(
            "Upload job description PDF",
            type=["pdf"],
            key="job_pdf",
        )

        if job_file:

            extracted_job = extract_pdf_text(
                job_file
            )

            with st.expander(
                "View extracted text",
                expanded=False,
            ):

                job_text = st.text_area(
                    "Extracted job description",
                    value=extracted_job,
                    height=300,
                    key="job_extracted",
                )


with right_column:

    st.markdown(
        '<h3><span class="step-badge">2</span> Your CV</h3>',
        unsafe_allow_html=True,
    )

    cv_input_method = st.radio(
        "Input method",
        ["Paste text", "Upload PDF"],
        key="cv_input_method",
        horizontal=True,
    )

    cv_text = ""

    if cv_input_method == "Paste text":

        cv_text = st.text_area(
            "Paste CV text",
            height=400,
            placeholder=(
                "Paste your CV here..."
            ),
        )

    else:

        cv_file = st.file_uploader(
            "Upload CV PDF",
            type=["pdf"],
            key="cv_pdf",
        )

        if cv_file:

            extracted_cv = extract_pdf_text(
                cv_file
            )

            with st.expander(
                "View extracted text",
                expanded=False,
            ):

                cv_text = st.text_area(
                    "Extracted CV",
                    value=extracted_cv,
                    height=300,
                    key="cv_extracted",
                )


st.divider()


analyze = st.button(
    "🔎 Analyze match",
    type="primary",
    use_container_width=True,
)


if analyze:

    job_text = clean_text(
        job_text
    )

    cv_text = clean_text(
        cv_text
    )

    if len(job_text) < 100:

        st.error(
            "Please provide a complete job description."
        )

        st.stop()

    if len(cv_text) < 100:

        st.error(
            "Please provide a complete CV."
        )

        st.stop()

    try:

        client = DatabricksSQL(
            settings.warehouse_id
        )

        with st.spinner(
            "Analyzing job and CV..."
        ):

            extracted = extract_job_candidate(
                client=client,
                endpoint=settings.ai_query_endpoint,
                job_text=job_text,
                cv_text=cv_text,
            )

        validate_result(
            extracted
        )

        with st.spinner(
            "Calculating match..."
        ):

            match = calculate_match(
                extracted
            )

        st.session_state[
            "analysis"
        ] = {
            "extracted":
                extracted,

            "match":
                match,
        }

        st.success(
            "Analysis completed."
        )

    except Exception as error:

        st.error(
            "Analysis failed."
        )

        st.exception(
            error
        )


analysis = st.session_state.get(
    "analysis"
)


if analysis:

    extracted = analysis[
        "extracted"
    ]

    match = analysis[
        "match"
    ]

    job = extracted[
        "job"
    ]

    candidate = extracted[
        "candidate"
    ]


    st.divider()

    st.markdown(
        '<div class="result-header"><span class="step-badge">3</span> Match result</div>',
        unsafe_allow_html=True,
    )


    # --- Score visualization ---

    def _score_color(score):
        if score >= 70:
            return "green"
        elif score >= 50:
            return "amber"
        return "red"

    overall = match["overall_score"]
    must_have = match["must_have_score"] or 0
    nice_to_have = match["nice_to_have_score"] or 0
    responsibility = match["responsibility_score"] or 0
    profile_fit = match.get("profile_fit_score") or 0
    big_color = "#059669" if overall >= 70 else "#d97706" if overall >= 50 else "#dc2626"

    st.markdown(
        f"""
    <div style="text-align: center; margin: 10px 0 24px;">
        <div style="font-size: 56px; font-weight: 800; line-height: 1; color: {big_color};">
            {overall:.0f}%
        </div>
        <div style="color: #475569; font-size: 14px; margin-top: 4px;">Overall match score</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    def _score_bar(label, value, color):
        return f"""
    <div style="margin-bottom: 14px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
            <span style="font-weight: 600; color: #0f172a; font-size: 14px;">{label}</span>
            <span style="font-weight: 700; color: #4f46e5; font-size: 14px;">{value:.0f}%</span>
        </div>
        <div class="score-bar-container">
            <div class="score-bar-fill {color}" style="width: {value}%"></div>
        </div>
    </div>
    """

    st.markdown(
        f"""
    <div style="margin: 0 0 24px;">
        {_score_bar("Must-have skills", must_have, _score_color(must_have))}
        {_score_bar("Nice-to-have skills", nice_to_have, _score_color(nice_to_have))}
        {_score_bar("Responsibilities", responsibility, _score_color(responsibility))}
        {_score_bar("Profile fit", profile_fit, _score_color(profile_fit))}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # --- Recommendation banner ---

    rec_class = "strong" if overall >= 80 else "reasonable" if overall >= 65 else "gaps" if overall >= 50 else "low"
    rec_icon = "✅" if overall >= 80 else "👍" if overall >= 65 else "⚠️" if overall >= 50 else "❌"

    st.markdown(
        f"""
    <div class="rec-banner {rec_class}">
        {rec_icon} {match["recommendation"]}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # --- Tabbed results ---

    tab_skills, tab_resp, tab_profile, tab_ats, tab_ai = st.tabs(
        ["🎯 Skills match", "📋 Responsibilities", "👤 Profile", "🔍 ATS keywords", "🤖 AI extraction"]
    )

    with tab_skills:
        st.subheader("Must-have skills")
        must_df = pd.DataFrame(match["must_have"])
        if not must_df.empty:
            must_df = must_df.rename(columns={
                "requirement": "Requirement",
                "candidate_match": "CV match",
                "similarity": "Similarity",
                "status": "Status",
            })
            must_df["Similarity"] = (must_df["Similarity"] * 100).round(1)
            st.dataframe(
                must_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Similarity": st.column_config.ProgressColumn(
                        min_value=0.0,
                        max_value=100.0,
                        format="%.0f%%",
                    ),
                },
            )
        st.subheader("Nice-to-have skills")
        nice_df = pd.DataFrame(match["nice_to_have"])
        if not nice_df.empty:
            nice_df = nice_df.rename(columns={
                "requirement": "Requirement",
                "candidate_match": "CV match",
                "similarity": "Similarity",
                "status": "Status",
            })
            nice_df["Similarity"] = (nice_df["Similarity"] * 100).round(1)
            st.dataframe(
                nice_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Similarity": st.column_config.ProgressColumn(
                        min_value=0.0,
                        max_value=100.0,
                        format="%.0f%%",
                    ),
                },
            )

    with tab_resp:
        responsibilities_df = pd.DataFrame(match["responsibilities"])
        if not responsibilities_df.empty:
            responsibilities_df = responsibilities_df.rename(columns={
                "requirement": "Job responsibility",
                "candidate_match": "CV evidence",
                "similarity": "Similarity",
                "status": "Status",
            })
            responsibilities_df["Similarity"] = (responsibilities_df["Similarity"] * 100).round(1)
            st.dataframe(
                responsibilities_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Similarity": st.column_config.ProgressColumn(
                        min_value=0.0,
                        max_value=100.0,
                        format="%.0f%%",
                    ),
                },
            )
        else:
            st.info("No responsibilities data available.")

    with tab_profile:
        st.subheader("Job profile")
        profile_data = {
            "Title": job.get("title"),
            "Company": job.get("company"),
            "Seniority": job.get("seniority"),
        }
        st.table(pd.DataFrame([profile_data]))
        st.subheader("Candidate skill evidence")
        evidence_df = pd.DataFrame(candidate["skills"])
        if not evidence_df.empty:
            st.dataframe(evidence_df, use_container_width=True, hide_index=True)
        else:
            st.info("No skill evidence available.")

    with tab_ats:
        missing_keywords = [
            item["requirement"]
            for item in match["must_have"]
            if item["status"] == "missing"
        ]
        if missing_keywords:
            st.warning("Potential missing keywords: " + ", ".join(missing_keywords))
            st.caption("Only add a keyword to your CV if it truthfully represents your experience.")
        else:
            st.success("No must-have skill gaps detected.")

    with tab_ai:
        st.json(extracted)


    if settings.save_enabled:

        st.divider()

        st.subheader(
            "Save analysis"
        )

    if (
        settings.save_enabled
        and st.button(
            "💾 Save analysis to Delta",
            use_container_width=True,
        )
    ):

        try:

            record = {

                "analysis_id":
                    str(uuid.uuid4()),

                "job_title":
                    job.get(
                        "title",
                        "",
                    ),

                "company":
                    job.get(
                        "company",
                        "",
                    ),

                "overall_score":
                    match[
                        "overall_score"
                    ],

                "recommendation":
                    match[
                        "recommendation"
                    ],

                "must_have_score":
                    match[
                        "must_have_score"
                    ] or 0,

                "nice_to_have_score":
                    match[
                        "nice_to_have_score"
                    ] or 0,

                "responsibility_score":
                    match[
                        "responsibility_score"
                    ] or 0,

                "profile_fit_score":
                    match[
                        "profile_fit_score"
                    ],

                "job":
                    job,

                "candidate":
                    candidate,

                "match":
                    match,
            }


            client = DatabricksSQL(
                settings.warehouse_id
            )

            client.save_analysis(
                settings.analysis_table,
                record,
            )

            st.success(
                "Analysis saved to Delta Lake."
            )

        except Exception as error:

            st.error(
                "Could not save analysis."
            )

            st.exception(
                error
            )


# --- Features ---

st.divider()

fc1, fc2, fc3 = st.columns(3)

with fc1:
    st.markdown(
        """
    <div class="feature-card">
        <div class="feature-icon blue">🔍</div>
        <h3>Analyze</h3>
        <p>AI extracts job requirements and your skills, then compares them side by side.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with fc2:
    st.markdown(
        """
    <div class="feature-card">
        <div class="feature-icon purple">📊</div>
        <h3>Score</h3>
        <p>Get an explainable match score with breakdown by must-have, nice-to-have, and responsibilities.</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

with fc3:
    if settings.save_enabled:
        card = """
    <div class="feature-card">
        <div class="feature-icon green">💾</div>
        <h3>Save</h3>
        <p>Store analyses in Delta Lake to track your job applications over time.</p>
    </div>
    """
    else:
        card = """
    <div class="feature-card">
        <div class="feature-icon green">📝</div>
        <h3>Decide</h3>
        <p>Get a clear recommendation on whether an application is worth pursuing.</p>
    </div>
    """
    st.markdown(card, unsafe_allow_html=True)

st.markdown(
    """
<div class="app-footer">
    Career Lens · Powered by Databricks
</div>
""",
    unsafe_allow_html=True,
)