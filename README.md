# Git Sync

GitHub ➡️ GitLab

## Prerequisites

Create GitHub[access token](https://github.com/settings/tokens/new) with `admin:public_key` and `repo` scope.

## Environment variables

Copy and rename `.env.sample` and update.

## Build Docker Image

```
docker build \
    --build-arg ssh_private_key="$(cat ~/.ssh/id_rsa)" \
    --build-arg ssh_public_key="$(cat ~/.ssh/id_rsa.pub)" \
    --tag git-sync . && \
docker run -it \
    --env-file=".env" \
    -v $PWD/repos:/app/repos \
    -v $PWD/logs:/app/logs \
    git-sync
```

## Format and Lint

```sh
autopep8 --in-place --recursive .
find . -type f -name "*.py" | xargs pylint
hadolint Dockerfile
dockerfilelint Dockerfile
```