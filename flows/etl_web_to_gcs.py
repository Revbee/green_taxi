import pandas as pd
from pathlib import Path
from prefect import flow, task
from prefect.tasks import task_input_hash
from prefect_gcp.cloud_storage import GcsBucket


@task(log_prints=True, retries=2)
def fetch_data(dataset_url: str) -> pd.DataFrame:
    df = pd.read_csv(dataset_url)
    return df


@task(log_prints=True)
def write_to_local(df: pd.DataFrame, color: str, dataset_file: str) -> Path:
    path = Path(f"data/{color}/{dataset_file}.parquet")
    df.to_parquet(path, compression="gzip")
    return path


@task(log_prints=True)
def write_to_gcs(path: Path) -> None:
    gcp_cloud_storage_bucket_block = GcsBucket.load("green-data-block")
    gcp_cloud_storage_bucket_block.upload_from_path(from_path=path, to_path=path)
    return


@flow()
def etl_web_to_gcp(color: str, year: int, month: int) -> None:
    dataset_file = f"{color}_tripdata_{year}-{month:02}"
    dataset_url = f"https://github.com/DataTalksClub/nyc-tlc-data/releases/download/{color}/{dataset_file}.csv.gz"
    df = fetch_data(dataset_url)
    path = write_to_local(df, color, dataset_file)
    write_to_gcs(path)


@flow()
def etl_parent_flow(color: str = "fhv", year: int = 2020, months: list[int] = [1, 2]):
    for month in months:
        etl_web_to_gcp(color, year, month)


if __name__ == "__main__":
    color = "fhv"
    year = 2020
    months = [1, 2, 3]
    etl_parent_flow(color, year, months)

# In[ ]
