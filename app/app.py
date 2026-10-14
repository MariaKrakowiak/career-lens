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
    page_title="Career Copilot",
    page_icon="🎯",
    layout="wide",
)


st.title(
    "🎯 Career Copilot"
)

st.caption(
    "Version 1 — CV ↔ Job Description analysis"
)


with st.sidebar:

    st.header(
        "Configuration"
    )

    try:

        settings = get_settings()

        st.success(
            "Databricks configuration loaded"
        )

    except Exception as error:

        st.error(
            str(error)
        )

        st.stop()


st.markdown(
    """
    ### What this application does

    Upload your CV and paste a job description.

    Career Copilot will:

    - extract job requirements
    - identify your skills
    - compare your experience with the role
    - identify missing skills
    - identify ATS keyword gaps
    - calculate an explainable match score
    - recommend whether the application is worth pursuing

    **Important:** this is a personal job-search assistant.
    It is not a hiring or candidate-selection system.
    """
)


left_column, right_column = st.columns(
    2
)


with left_column:

    st.subheader(
        "1. Job description"
    )

    job_file = st.file_uploader(
        "Upload job description PDF",
        type=["pdf"],
        key="job_pdf",
    )

    job_text = st.text_area(
        "Paste job description",
        height=400,
        placeholder=(
            "Paste the complete job description here..."
        ),
    )

    if job_file:

        extracted_job = extract_pdf_text(
            job_file
        )

        job_text = st.text_area(
            "Extracted job description",
            value=extracted_job,
            height=300,
            key="job_extracted",
        )


with right_column:

    st.subheader(
        "2. Your CV"
    )

    cv_file = st.file_uploader(
        "Upload CV PDF",
        type=["pdf"],
        key="cv_pdf",
    )

    cv_text = st.text_area(
        "Paste CV text",
        height=400,
        placeholder=(
            "Paste your CV here..."
        ),
    )

    if cv_file:

        extracted_cv = extract_pdf_text(
            cv_file
        )

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

    st.header(
        "3. Match result"
    )


    col1, col2, col3 = st.columns(
        3
    )

    col1.metric(
        "Overall match",
        f'{match["overall_score"]:.0f}%',
    )

    col2.metric(
        "Must-have skills",
        (
            f'{match["must_have_score"]:.0f}%'
            if match["must_have_score"]
            is not None
            else "N/A"
        ),
    )

    col3.metric(
        "Responsibilities",
        (
            f'{match["responsibility_score"]:.0f}%'
            if match[
                "responsibility_score"
            ]
            is not None
            else "N/A"
        ),
    )


    if match[
        "overall_score"
    ] >= 65:

        st.success(
            match[
                "recommendation"
            ]
        )

    else:

        st.warning(
            match[
                "recommendation"
            ]
        )


    st.subheader(
        "Job profile"
    )

    profile_data = {

        "Title":
            job.get(
                "title"
            ),

        "Company":
            job.get(
                "company"
            ),

        "Seniority":
            job.get(
                "seniority"
            ),
    }

    st.table(
        pd.DataFrame(
            [profile_data]
        )
    )


    st.subheader(
        "Must-have skills"
    )

    must_df = pd.DataFrame(
        match[
            "must_have"
        ]
    )

    if not must_df.empty:

        must_df = must_df.rename(
            columns={
                "requirement":
                    "Requirement",

                "candidate_match":
                    "CV match",

                "similarity":
                    "Similarity",

                "status":
                    "Status",
            }
        )

        st.dataframe(
            must_df,
            use_container_width=True,
            hide_index=True,
        )


    st.subheader(
        "Nice-to-have skills"
    )

    nice_df = pd.DataFrame(
        match[
            "nice_to_have"
        ]
    )

    if not nice_df.empty:

        nice_df = nice_df.rename(
            columns={
                "requirement":
                    "Requirement",

                "candidate_match":
                    "CV match",

                "similarity":
                    "Similarity",

                "status":
                    "Status",
            }
        )

        st.dataframe(
            nice_df,
            use_container_width=True,
            hide_index=True,
        )


    st.subheader(
        "Responsibilities"
    )

    responsibilities_df = pd.DataFrame(
        match[
            "responsibilities"
        ]
    )

    if not responsibilities_df.empty:

        responsibilities_df = (
            responsibilities_df.rename(
                columns={
                    "requirement":
                        "Job responsibility",

                    "candidate_match":
                        "CV evidence",

                    "similarity":
                        "Similarity",

                    "status":
                        "Status",
                }
            )
        )

        st.dataframe(
            responsibilities_df,
            use_container_width=True,
            hide_index=True,
        )


    st.subheader(
        "ATS keyword gaps"
    )

    missing_keywords = [

        item[
            "requirement"
        ]

        for item
        in match[
            "must_have"
        ]

        if item[
            "status"
        ] == "missing"
    ]


    if missing_keywords:

        st.warning(
            "Potential missing keywords: "
            +
            ", ".join(
                missing_keywords
            )
        )

        st.caption(
            "Only add a keyword to your CV if it truthfully "
            "represents your experience."
        )

    else:

        st.success(
            "No must-have skill gaps detected."
        )


    st.subheader(
        "Candidate skill evidence"
    )

    evidence_df = pd.DataFrame(
        candidate[
            "skills"
        ]
    )

    if not evidence_df.empty:

        st.dataframe(
            evidence_df,
            use_container_width=True,
            hide_index=True,
        )


    st.subheader(
        "Application recommendation"
    )

    if match[
        "overall_score"
    ] >= 80:

        st.success(
            """
            This appears to be a strong match.
            The application should be a high priority.
            """
        )

    elif match[
        "overall_score"
    ] >= 65:

        st.info(
            """
            This appears to be a reasonable match.
            Applying is likely worth considering.
            """
        )

    elif match[
        "overall_score"
    ] >= 50:

        st.warning(
            """
            There are meaningful gaps.
            Consider the importance of those gaps before applying.
            """
        )

    else:

        st.error(
            """
            There appear to be significant gaps.
            This application may be lower priority.
            """
        )


    with st.expander(
        "Show structured AI extraction"
    ):

        st.json(
            extracted
        )


    st.divider()

    st.subheader(
        "Save analysis"
    )

    if st.button(
        "💾 Save analysis to Delta",
        use_container_width=True,
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