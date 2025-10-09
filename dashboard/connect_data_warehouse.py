from pathlib import Path
import duckdb
import pandas as pd

# data warehouse directory
db_path = str(Path(__file__).parents[1] / "data_warehouse/job_ads.duckdb")

def query_all_job_listings():
    tables = [
        "MART_BYGG_OCH_ANLAGGNING",
        "MART_KULTUR_MEDIA_DESIGN",
        "MART_PEDAGOGIK"
    ]

    data = {}
   
    with duckdb.connect(db_path, read_only=True) as conn:
       
           for table in tables:
            query = f"""
                SELECT *
                FROM {table}
            """
            df = pd.read_sql(query, conn)
            data[table] = df

    return data
all_data = query_all_job_listings()
df_bygg = all_data["MART_BYGG_OCH_ANLAGGNING"]
df_kultur = all_data["MART_KULTUR_MEDIA_DESIGN"]
df_pedagogik = all_data["MART_PEDAGOGIK"]

print(df_bygg.head())
print(df_kultur.head())
print(df_pedagogik.head())