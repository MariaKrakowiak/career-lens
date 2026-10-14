import re
from difflib import SequenceMatcher


STOP_WORDS = {
    "experience",
    "knowledge",
    "skills",
    "skill",
    "ability",
    "strong",
    "good",
    "working",
    "understanding",
    "using",
    "use",
    "years",
    "year",
    "required",
    "preferred",
    "excellent",
}


def normalize(text: str) -> str:

    text = text.lower().strip()

    text = text.replace(
        "&",
        " and ",
    )

    text = re.sub(
        r"[^a-z0-9+#.\- ]+",
        " ",
        text,
    )

    text = re.sub(
        r"\s+",
        " ",
        text,
    )

    return text


def tokens(text: str):

    return {
        token
        for token in normalize(text).split()

        if (
            len(token) > 2
            and token not in STOP_WORDS
        )
    }


def similarity(
    first: str,
    second: str,
) -> float:

    first_normalized = normalize(first)
    second_normalized = normalize(second)

    if (
        first_normalized
        == second_normalized
    ):
        return 1.0

    if (
        first_normalized in second_normalized
        or
        second_normalized in first_normalized
    ):
        return 0.9

    first_tokens = tokens(first)
    second_tokens = tokens(second)

    if not first_tokens or not second_tokens:
        return 0.0

    intersection = (
        first_tokens
        & second_tokens
    )

    union = (
        first_tokens
        | second_tokens
    )

    jaccard = (
        len(intersection)
        /
        len(union)
    )

    sequence = SequenceMatcher(
        None,
        first_normalized,
        second_normalized,
    ).ratio()

    return max(
        jaccard,
        sequence * 0.85,
    )


def best_match(
    requirement: str,
    candidates: list[str],
):

    if not candidates:
        return None, 0.0

    scored = []

    for candidate in candidates:

        score = similarity(
            requirement,
            candidate,
        )

        scored.append(
            (
                candidate,
                score,
            )
        )

    return max(
        scored,
        key=lambda x: x[1],
    )


def coverage(
    requirements: list[str],
    candidates: list[str],
    threshold: float = 0.72,
):

    rows = []

    for requirement in requirements:

        candidate_match, score = best_match(
            requirement,
            candidates,
        )

        if score >= 0.88:

            status = "strong"

        elif score >= threshold:

            status = "partial"

        else:

            status = "missing"

        rows.append(
            {
                "requirement": requirement,
                "candidate_match": candidate_match,
                "similarity": round(
                    score,
                    3,
                ),
                "status": status,
            }
        )

    if not requirements:

        return rows, None

    weighted_coverage = sum(

        1.0
        if row["status"] == "strong"

        else 0.5
        if row["status"] == "partial"

        else 0.0

        for row in rows
    )

    score = (
        weighted_coverage
        /
        len(requirements)
        *
        100
    )

    return rows, round(
        score,
        1,
    )


def calculate_match(
    result: dict,
) -> dict:

    job = result["job"]
    candidate = result["candidate"]

    candidate_skills = [
        item["skill"]
        for item in candidate["skills"]
    ]

    must_have, must_have_score = coverage(
        job["must_have_skills"],
        candidate_skills,
    )

    nice_to_have, nice_to_have_score = coverage(
        job["nice_to_have_skills"],
        candidate_skills,
    )

    candidate_responsibilities = [
        item["responsibility"]
        for item
        in candidate[
            "responsibility_evidence"
        ]
    ]

    responsibilities, responsibility_score = coverage(
        job["responsibilities"],
        candidate_responsibilities,
        threshold=0.60,
    )

    profile_fit_score = 100.0

    job_seniority = normalize(
        job.get(
            "seniority",
            "",
        )
    )

    candidate_seniority = normalize(
        candidate.get(
            "seniority",
            "",
        )
    )

    if (
        job_seniority
        and candidate_seniority
    ):

        seniority_similarity = similarity(
            job_seniority,
            candidate_seniority,
        )

        if seniority_similarity < 0.65:
            profile_fit_score = 50.0

    values = []
    weights = []

    if must_have_score is not None:

        values.append(
            must_have_score
        )

        weights.append(
            0.45
        )

    if nice_to_have_score is not None:

        values.append(
            nice_to_have_score
        )

        weights.append(
            0.20
        )

    if responsibility_score is not None:

        values.append(
            responsibility_score
        )

        weights.append(
            0.20
        )

    values.append(
        profile_fit_score
    )

    weights.append(
        0.15
    )

    weight_sum = sum(weights)

    overall_score = (
        sum(
            value * weight
            for value, weight
            in zip(values, weights)
        )
        /
        weight_sum
    )

    overall_score = round(
        overall_score,
        1,
    )

    if overall_score >= 80:

        recommendation = (
            "APPLY — strong match"
        )

    elif overall_score >= 65:

        recommendation = (
            "APPLY — reasonable match"
        )

    elif overall_score >= 50:

        recommendation = (
            "CONSIDER — meaningful gaps"
        )

    else:

        recommendation = (
            "LOW PRIORITY — significant gaps"
        )

    return {

        "overall_score":
            overall_score,

        "recommendation":
            recommendation,

        "must_have_score":
            must_have_score,

        "nice_to_have_score":
            nice_to_have_score,

        "responsibility_score":
            responsibility_score,

        "profile_fit_score":
            profile_fit_score,

        "must_have":
            must_have,

        "nice_to_have":
            nice_to_have,

        "responsibilities":
            responsibilities,
    }