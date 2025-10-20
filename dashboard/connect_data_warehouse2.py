from pathlib import Path
import duckdb
import pandas as pd
import os

# data warehouse directory
#DB_PATH= os.getenv("DUCKDB_PATH")  
FILES_SHARE_PATH = Path("/mnt/data/job_ads.duckdb") 
def query_all_job_listings():
    tables = [
        "MART_BYGG_OCH_ANLAGGNING",
        "MART_KULTUR_MEDIA_DESIGN",
        "MART_PEDAGOGIK"
    ]

    data = {}
   
    with duckdb.connect(FILES_SHARE_PATH, read_only=True) as conn:
       
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