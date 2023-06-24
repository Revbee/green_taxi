from prefect.infrastructure.container import DockerContainer
from prefect.deployments import Deployment
from prefect.filesystems import GitHub
from etl_web_to_gcs import etl_parent_flow

github_block = GitHub.load("git-block")
docker_container_block = DockerContainer.load("etl-pipline")

docker_dep = Deployment.build_from_flow(
    flow=etl_parent_flow,
    name="docker-flow",
    infrastructure=docker_container_block,
    storage=github_block,
)

if __name__ == "__main__":
    docker_dep.apply()
