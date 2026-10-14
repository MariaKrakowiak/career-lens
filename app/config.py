import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:

    warehouse_id: str
    ai_query_endpoint: str

    catalog: str
    schema: str

    @property
    def analysis_table(self) -> str:
        return (
            f"{self.catalog}."
            f"{self.schema}."
            f"analyses"
        )


def get_settings() -> Settings:

    warehouse_id = os.getenv(
        "DATABRICKS_WAREHOUSE_ID"
    )

    ai_query_endpoint = os.getenv(
        "AI_QUERY_ENDPOINT"
    )

    catalog = os.getenv(
        "UC_CATALOG",
        "main"
    )

    schema = os.getenv(
        "UC_SCHEMA",
        "career_lens"
    )

    missing = []

    if not warehouse_id:
        missing.append(
            "DATABRICKS_WAREHOUSE_ID"
        )

    if not ai_query_endpoint:
        missing.append(
            "AI_QUERY_ENDPOINT"
        )

    if missing:
        raise RuntimeError(
            "Missing environment variables: "
            + ", ".join(missing)
        )

    return Settings(
        warehouse_id=warehouse_id,
        ai_query_endpoint=ai_query_endpoint,
        catalog=catalog,
        schema=schema,
    )