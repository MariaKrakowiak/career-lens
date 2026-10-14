SELECT ai_query(
    'system.ai.meta-llama-3-3-70b-instruct',
    'Return exactly the word hello.'
) AS response;

SELECT ai_query(
    'system.ai.meta-llama-3-3-70b-instruct',
    'Extract the technical skills from this job description. Return only a comma-separated list: We are looking for a Data Engineer with Python, SQL, Apache Spark, Databricks and AWS.'
) AS response;

SELECT ai_query(
    'system.ai.meta-llama-3-3-70b-instruct',

    'Analyze this job description:
     We are looking for a Senior Data Engineer.
     The candidate must know Python, SQL, Apache Spark and Databricks.
     AWS is preferred.
     The person will build and maintain scalable data pipelines.',

    responseFormat => '{
      "type": "json_schema",
      "json_schema": {
        "name": "job_extraction",
        "schema": {
          "type": "object",
          "properties": {
            "title": {
              "type": "string"
            },
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
            }
          },
          "required": [
            "title",
            "must_have_skills",
            "nice_to_have_skills",
            "responsibilities"
          ],
          "additionalProperties": false
        },
        "strict": true
      }
    }'
) AS response;

SELECT current_catalog();