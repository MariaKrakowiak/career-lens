from app.matcher import (
    calculate_match,
    similarity,
)


def test_exact_similarity():

    assert (
        similarity(
            "Python",
            "Python",
        )
        == 1.0
    )


def test_python_is_detected():

    data = {

        "job": {

            "must_have_skills": [
                "Python",
                "SQL",
            ],

            "nice_to_have_skills": [],

            "responsibilities": [],

            "seniority": "Mid",
        },

        "candidate": {

            "skills": [

                {
                    "skill": "Python",

                    "evidence":
                        "Built Python services",

                    "evidence_type":
                        "explicit",
                },

                {
                    "skill": "SQL",

                    "evidence":
                        "Used SQL daily",

                    "evidence_type":
                        "explicit",
                },
            ],

            "responsibility_evidence": [],

            "seniority": "Mid",

            "education": [],

            "languages": [],
        },
    }


    result = calculate_match(
        data
    )


    assert (
        result[
            "must_have_score"
        ]
        == 100.0
    )


def test_missing_skill():

    data = {

        "job": {

            "must_have_skills": [
                "Kubernetes"
            ],

            "nice_to_have_skills": [],

            "responsibilities": [],

            "seniority": "",
        },

        "candidate": {

            "skills": [],

            "responsibility_evidence": [],

            "seniority": "",

            "education": [],

            "languages": [],
        },
    }


    result = calculate_match(
        data
    )


    assert (
        result[
            "must_have_score"
        ]
        == 0.0
    )


    assert (
        result[
            "must_have"
        ][0][
            "status"
        ]
        == "missing"
    )