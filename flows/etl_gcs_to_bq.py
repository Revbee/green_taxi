import pandas as pd
from pathlib import Path
from prefect import flow, task
from prefect.tasks import task_input_hash
from prefect_gcp.cloud_storage import GcsBucket
from prefect_gcp import GcpCredentials


@task(retries=3, log_prints=True)
def extract_from_gcs(color: str, year: int, month: int) -> Path:
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    gcs_path = f"data/{color}/{dataset_file}.parquet"
    gcp_cloud_storage_bucket_block = GcsBucket.load("green-data-block")
    gcp_cloud_storage_bucket_block.get_directory(
        from_path=gcs_path, local_path=f"data/{color}/"
    )
    return Path(f"{gcs_path}")


@task(log_prints=True)
def transform(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    return df


@task(log_prints=True)
def write_to_bq(df: pd.DataFrame) -> int:
    gcp_credentials_block = GcpCredentials.load("week2gcp-credentials")
    df.to_gbq(
        destination_table="Week2_Dataset.green",
        project_id="titanium-scope-389619",
        chunksize=500_000,
        if_exists="append",
    )
    return len(df)


@flow()
def etl_gcp_to_web(color: str, year: int, month: int) -> int:
    path = extract_from_gcs(color, year, month)
    df = transform(path)
    row_count = write_to_bq(df)
    return row_count


@flow(log_prints=True)
def etl_parent_flow(color: str = "green", year: int = 2020, months: list[int] = [1, 2]):
    total_rows = 0
    for month in months:
        row = etl_gcp_to_web(color, year, month)
        total_rows += row
        print(f"the total row count is {total_rows}")


if __name__ == "__main__":
    color = "green"
    year = 2020
    months = [1, 2, 3]
    etl_parent_flow(color, year, months)
