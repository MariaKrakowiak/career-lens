import json

from databricks import sql
from databricks.sdk.core import Config


class DatabricksSQL:

    def __init__(self, warehouse_id: str):

        self.config = Config()

        self.server_hostname = (
            self.config.host.replace(
                "https://",
                ""
            )
        )

        self.http_path = (
            f"/sql/1.0/warehouses/"
            f"{warehouse_id}"
        )

    def connection(self):

        return sql.connect(
            server_hostname=self.server_hostname,
            http_path=self.http_path,
            credentials_provider=(
                lambda: self.config.authenticate
            ),
        )

    def ai_query(
        self,
        endpoint: str,
        prompt: str,
    ) -> str:

        query = """
        SELECT ai_query(
            ?,
            ?
        ) AS response
        """

        with self.connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    (
                        endpoint,
                        prompt,
                    ),
                )

                row = cursor.fetchone()

                if row is None:
                    raise RuntimeError(
                        "ai_query returned no result."
                    )

                return row[0]

    def save_analysis(
        self,
        table_name: str,
        record: dict,
    ) -> None:

        query = f"""
        INSERT INTO {table_name}
        (
            analysis_id,
            created_at,
            job_title,
            company,
            overall_score,
            recommendation,
            must_have_score,
            nice_to_have_score,
            responsibility_score,
            profile_fit_score,
            job_json,
            candidate_json,
            match_json
        )
        VALUES (
            ?,
            current_timestamp(),
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?,
            ?
        )
        """

        values = (
            record["analysis_id"],
            record["job_title"],
            record["company"],
            record["overall_score"],
            record["recommendation"],
            record["must_have_score"],
            record["nice_to_have_score"],
            record["responsibility_score"],
            record["profile_fit_score"],
            json.dumps(
                record["job"],
                ensure_ascii=False,
            ),
            json.dumps(
                record["candidate"],
                ensure_ascii=False,
            ),
            json.dumps(
                record["match"],
                ensure_ascii=False,
            ),
        )

        with self.connection() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    query,
                    values,
                )