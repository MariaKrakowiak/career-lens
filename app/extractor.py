import json

from prompts import build_extraction_prompt


RESPONSE_SCHEMA = """
{
  "type": "json_schema",
  "json_schema": {
    "name": "career_lens_extraction",
    "schema": {
      "type": "object",
      "properties": {
        "job": {
          "type": "object",
          "properties": {
            "title": {"type": "string"},
            "company": {"type": "string"},
            "seniority": {"type": "string"},
            "must_have_skills": {
              "type": "array",
              "items": {"type": "string"}
            },
            "nice_to_have_skills": {
              "type": "array",
              "items": {"type": "string"}
            },
            "responsibilities": {
              "type": "array",
              "items": {"type": "string"}
            },
            "education_requirements": {
              "type": "array",
              "items": {"type": "string"}
            },
            "language_requirements": {
              "type": "array",
              "items": {"type": "string"}
            }
          },
          "required": [
            "title",
            "company",
            "seniority",
            "must_have_skills",
            "nice_to_have_skills",
            "responsibilities",
            "education_requirements",
            "language_requirements"
          ],
          "additionalProperties": false
        },
        "candidate": {
          "type": "object",
          "properties": {
            "skills": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "skill": {"type": "string"},
                  "evidence": {"type": "string"},
                  "evidence_type": {
                    "type": "string",
                    "enum": ["explicit", "inferred"]
                  }
                },
                "required": [
                  "skill",
                  "evidence",
                  "evidence_type"
                ],
                "additionalProperties": false
              }
            },
            "responsibility_evidence": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "responsibility": {"type": "string"},
                  "evidence": {"type": "string"},
                  "evidence_type": {
                    "type": "string",
                    "enum": ["explicit", "inferred"]
                  }
                },
                "required": [
                  "responsibility",
                  "evidence",
                  "evidence_type"
                ],
                "additionalProperties": false
              }
            },
            "education": {
              "type": "array",
              "items": {"type": "string"}
            },
            "languages": {
              "type": "array",
              "items": {"type": "string"}
            },
            "seniority": {"type": "string"}
          },
          "required": [
            "skills",
            "responsibility_evidence",
            "education",
            "languages",
            "seniority"
          ],
          "additionalProperties": false
        }
      },
      "required": ["job", "candidate"],
      "additionalProperties": false
    },
    "strict": true
  }
}
"""


def extract_job_candidate(
    client,
    endpoint: str,
    job_text: str,
    cv_text: str
) -> dict:
    prompt = build_extraction_prompt(
        job_text=job_text,
        cv_text=cv_text,
    )

    query = """
    SELECT ai_query(
        ?,
        ?,
        responseFormat => ?
    ) AS response
    """

    with client.connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                query,
                (
                    endpoint,
                    prompt,
                    RESPONSE_SCHEMA,
                ),
            )
            row = cursor.fetchone()

    if row is None:
        raise RuntimeError(
            "The AI model returned no response."
        )

    raw_response = row[0]

    if isinstance(raw_response, dict):
        return raw_response

    try:
        return json.loads(raw_response)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "The AI model did not return valid JSON.\n\n"
            f"Response:\n{raw_response}"
        ) from exc


def validate_result(result: dict) -> None:
    if not isinstance(result, dict):
        raise ValueError(
            "Extraction result must be a dictionary."
        )

    if "job" not in result:
        raise ValueError(
            "Extraction result is missing 'job'."
        )

    if "candidate" not in result:
        raise ValueError(
            "Extraction result is missing 'candidate'."
        )

    required_job_fields = [
        "title",
        "company",
        "seniority",
        "must_have_skills",
        "nice_to_have_skills",
        "responsibilities",
        "education_requirements",
        "language_requirements",
    ]

    required_candidate_fields = [
        "skills",
        "responsibility_evidence",
        "education",
        "languages",
        "seniority",
    ]

    for field in required_job_fields:
        if field not in result["job"]:
            raise ValueError(
                f"Job extraction is missing '{field}'."
            )

    for field in required_candidate_fields:
        if field not in result["candidate"]:
            raise ValueError(
                f"Candidate extraction is missing '{field}'."
            )