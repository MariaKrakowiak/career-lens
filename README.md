# 🎯 Career Lens

> ✨ An AI-powered job-matching assistant built with **Databricks** —
> compare a CV with a job description, get an explainable match score,
> skill gaps and an application recommendation, all in one web UI.

## 🔭 Overview

The application helps job seekers:

- 🔎 **analyze the match** — compare a CV with a job description side by side
- 📄 **flexible input** — paste plain text or upload a PDF for both documents
- 📊 **explainable score** — overall match with must-have, nice-to-have, responsibility and profile-fit breakdown
- 🧩 **skill gaps** — missing skills and ATS keyword gaps at a glance
- 📝 **recommendation** — whether the application is worth pursuing
- 💾 **save analyses** — store results in Delta Lake to track applications over time

The project is designed as a **personal job-search assistant**, not as a
hiring or candidate-selection system.

## 🏗️ Architecture

```
CV + Job Description 📄
      |
      v
Streamlit App 🎨
      |
      v
Databricks SQL Warehouse ⚙️
      |
      v
ai_query() — structured extraction 🤖
      |
      v
Job requirements + Candidate evidence 🧠
      |
      v
Deterministic matcher 🧮
      |
      v
Match report + recommendation 📊
      |
      v
Delta Lake (workspace.career_lens.analyses) 🗄️
```

## 🛠️ Technologies

- 🎨 **Streamlit** — web UI
- 🐍 **Python** — application logic and deterministic matching
- ⚙️ **Databricks SQL Warehouse** — AI function execution
- 🤖 **Databricks AI Functions** — `ai_query` for structured extraction
- 🗄️ **Delta Lake** + **Unity Catalog** — analysis storage
- 📄 **PyPDF** — PDF text extraction

## 🔑 Requirements

1. 🧱 Databricks workspace with Unity Catalog
2. ⚙️ SQL Warehouse that supports `ai_query`
3. 🤖 Model endpoint accessible through `ai_query`
4. 🎨 Databricks Apps (for the hosted deployment)

## 🤖 Model

The model endpoint is configured with the `AI_QUERY_ENDPOINT` environment
variable, for example:

```bash
system.ai.meta-llama-3-3-70b-instruct
```

Use any model-serving endpoint available in your workspace — do not
hard-code a model your workspace does not provide.

## 🗄️ Unity Catalog

Analyses are stored in:

```
catalog: workspace
schema:  career_lens
table:   workspace.career_lens.analyses
```

Create the schema and table with `sql/001_create_tables.sql`, or point
the application at a different catalog and schema through the
`UC_CATALOG` and `UC_SCHEMA` environment variables.

## 📦 Installation

Install the Python dependencies:

```bash
pip install -r app/requirements.txt
```

## 🚀 Databricks deployment

The application source lives in the `app/` folder and is deployed as a
Databricks App:

```bash
databricks apps deploy career-lens --source-code-path <repo>/app
```

Configuration is injected through `app.yaml` environment variables, with
the SQL Warehouse bound through the `sql-warehouse` resource — no
workspace-specific identifiers are stored in the repository.

## 🌍 External deployment

The app is also deployed on Render for public access:

🔗 **https://career-lens-u45j.onrender.com/**

All configuration is provided through environment variables
(`DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_WAREHOUSE_ID`,
`AI_QUERY_ENDPOINT`, `UC_CATALOG`, `UC_SCHEMA`). Keep the access token
in the host's secret store — never in the repository.

## 🔮 Future versions

The project uses versioned branches:

- ✅ **v1** — current stable version
- 🚧 **master** — active development line

New functionality will be developed on `master` and feature branches.
When a new version reaches a stable, deployable state, it will be
snapshotted as `v2`, `v3`, and so on.

## ✅ Project requirements

This project demonstrates:

- ✅ Databricks Apps
- ✅ Databricks SQL Warehouse
- ✅ Unity Catalog
- ✅ Databricks AI Functions (`ai_query`)
- ✅ Delta Lake
- ✅ Unstructured text processing (PDF extraction)
- ✅ Streamlit web UI
- ✅ Deterministic, explainable matching
- ✅ External deployment (Render)