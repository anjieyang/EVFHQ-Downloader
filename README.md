# EVFHQ-Downloader

EVFHQ-Downloader handles the downloading of video files from YouTube.

## DockerHub Repository

You can find the [Docker image](https://hub.docker.com/repository/docker/anjieyang/evfhq-downloader/general) for EVFHQ-Downloader on DockerHub.

## Deployment Configurations

### Local Build Deployment with Docker Compose

For deploying EVFHQ-Downloader using Docker Compose and building the Docker image locally, you can use the provided `docker-compose.yml` file.

### DockerHub Deployment

If you prefer a quick and straightforward deployment using the Docker image from DockerHub.

1. Download [dockerhub_deploy.yml](https://drive.google.com/uc?export=download&id=1-j1V0hJ-XvDZNRAO5kSr9wVOWTOhT_WD).

2. Replace the placeholder values (`your_rabbitmq_host`, `your_docker_save_dir`, `your_machine_save_dir`, `your_docker_save_dir`) with your actual configurations.

3. Run the following command to start the EVFHQ-Fetcher service:

```bash
docker-compose -f dockerhub_deploy.yml up -d
```
