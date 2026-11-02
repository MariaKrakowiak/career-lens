CREATE SCHEMA IF NOT EXISTS career_lens;

CREATE TABLE IF NOT EXISTS career_lens.analyses
(
    analysis_id STRING,
    created_at TIMESTAMP,
    job_title STRING,
    company STRING,
    overall_score DOUBLE,
    recommendation STRING,
    must_have_score DOUBLE,
    nice_to_have_score DOUBLE,
    responsibility_score DOUBLE,
    profile_fit_score DOUBLE,
    job_json STRING,
    candidate_json STRING,
    match_json STRING
)
USING DELTA;
