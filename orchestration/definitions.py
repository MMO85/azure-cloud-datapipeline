from pathlib import Path
import dlt
import dagster as dg
#from dagster_dlt import dlt_resource, dlt_source
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets
from dagster import Definitions
from dagster_dlt import dlt_assets, DagsterDltResource
import sys
import os

DUCKDB_PATH = os.getenv("DUCKDB_PATH")
DBT_PROFILES_DIR = os.getenv("DBT_PROFILES_DIR")
#db_path = str(Path(__file__).parents[1] / "data_warehouse/job_ads.duckdb")
sys.path.insert(0, "../data_extract_load")
from load_data_jobs import jobsearch_source

#dlt assets
dlt_resource = DagsterDltResource()

@dlt_assets(
    dlt_source = jobsearch_source(),
    dlt_pipeline= dlt.pipeline(
        pipeline_name="HRpipeline",
        dataset_name="staging",
        destination=dlt.destinations.duckdb(DUCKDB_PATH)
    
    )
)
def dlt_load(context:dg.AssetExecutionContext, dlt:DagsterDltResource):
    yield from dlt.run(context=context)
    


dbt_project_directory = Path(__file__).parents[1] / "data_transformation" 



dbt_project = DbtProject(project_dir=dbt_project_directory, profiles_dir=Path(DBT_PROFILES_DIR))

#CLI commands e.g. dbt build, dbt run, dbt test
dbt_resource=DbtCliResource(project_dir= dbt_project)   

dbt_project.prepare_if_dev()

#dbt assets

@dbt_assets(manifest=dbt_project.manifest_path)
def dbt_models(context: dg.AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"],context=context).stream()
    

#jobs
job_dlt = dg.define_asset_job("job_dlt", selection=dg.AssetSelection.keys("dlt_jobsearch_source_jobsearch_resource"))

job_dbt = dg.define_asset_job("job_dbt", selection=dg.AssetSelection.key_prefixes("DWH","marts"))


schedule_dlt = dg.ScheduleDefinition(job=job_dlt, cron_schedule="0 9 * * MON")  # every Monday at 9am
@dg.asset_sensor(job=job_dbt, asset_key=dg.AssetKey("dlt_jobsearch_source_jobsearch_resource"))

def dlt_load_sensor():
    yield dg.RunRequest()
    

#definitions
defs = dg.Definitions(
    assets=[dlt_load, dbt_models],
    resources={"dlt": dlt_resource, "dbt": dbt_resource},
    jobs=[job_dlt, job_dbt],
    schedules=[schedule_dlt],
    sensors=[dlt_load_sensor]
)