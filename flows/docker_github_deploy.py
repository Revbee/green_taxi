from prefect.infrastructure.container import DockerContainer
from prefect.filesystems import GitHub
from prefect.deployments import Deployment
from etl_web_to_gcs import etl_parent_flow

docker_container_block = DockerContainer.load("etl-pipline")

github_block = GitHub.load("git-block")

docker_dep = Deployment.build_from_flow(
    flow=etl_parent_flow, name="docker-flow", infrastructure=docker_container_block
)

github_block.get_directory("flows")

if __name__ == "__main__":
    docker_dep.apply()
