# Career Copilot V1

Personal AI recruitment assistant built with Databricks.

The application compares a candidate's CV with a job description and produces:

- overall match score
- must-have skill coverage
- nice-to-have skill coverage
- responsibility coverage
- candidate evidence
- missing skills
- ATS keyword gaps
- application recommendation

The project is designed as a personal job-search assistant, not as a hiring decision system.

---

## Architecture

CV + Job Description
        |
        v
+-----------------------+
| Streamlit Application |
+-----------+-----------+
            |
            v
+-----------------------+
| Databricks SQL        |
| ai_query()            |
+-----------+-----------+
            |
            v
+-----------------------+
| Structured extraction |
| Job + Candidate       |
+-----------+-----------+
            |
            v
+-----------------------+
| Deterministic matcher |
+-----------+-----------+
            |
            v
+-----------------------+
| Match report          |
+-----------------------+

---

## Technologies

- Databricks
- Databricks SQL Warehouse
- Unity Catalog
- Databricks AI Functions
- `ai_query`
- Streamlit
- Python
- Delta Lake
- PyPDF

---

## Requirements

You need:

1. Databricks workspace
2. Unity Catalog
3. SQL Warehouse
4. Model Serving / Foundation Model endpoint accessible through `ai_query`
5. Databricks Apps

The SQL Warehouse must support `ai_query`.

---

## Model

The model endpoint is configured through:

AI_QUERY_ENDPOINT

For example:

system.ai.gpt-oss-20b

or another model-serving endpoint available in your workspace.

Do not hard-code a model that your workspace does not provide.

---

## Unity Catalog

The project creates:

catalog:
main

schema:
career_copilot

table:
main.career_copilot.analyses

Change these values if necessary.

---

## Installation

Install the Python dependencies:

```bash
pip install -r app/requirements.txt