# connect_data_warehouse.py
import os
from pathlib import Path
import duckdb
import pandas as pd

# در Azure از App Settings مقدار بده: DUCKDB_PATH=/mounts/hrshare/job_ads.duckdb
DB_PATH = os.getenv("DUCKDB_PATH", "/mnt/data/job_ads.duckdb")

def _connect_ro():
    p = Path(DB_PATH)
    if not p.exists():
        raise FileNotFoundError(f"DuckDB file not found: {p}")
    return duckdb.connect(str(p), read_only=True)

def query_job_listings() -> pd.DataFrame:
    """
    داده‌ی مارت «bygg och anläggning» را لود می‌کند.
    جدول: marts.mart_bygg_och_anlaggning
    """
    with _connect_ro() as conn:
        # اگر نام ستون‌ها کمی تفاوت داشت، این SELECT آن‌ها را به نام‌های مورد انتظار نگاشت می‌کند
        q = """
        SELECT
            COALESCE(vacancies, 0)                      AS vacancies,
            occupation                                  AS occupation,
            occupation_field                            AS occupation_field,
            CAST(application_deadline AS DATE)          AS application_deadline,
            headline                                    AS headline,
            job_description                              AS job_description,
            job_description_html                         AS job_description_html,
            employer_name                                AS employer_name,
            employment_type                              AS employment_type,
            salary_type                                  AS salary_type,
            duration                                     AS duration,
            workplace_region                             AS workplace_region,
            job_description_id                           AS job_description_id
        FROM marts.mart_bygg_och_anlaggning
        """
        return conn.execute(q).df()
