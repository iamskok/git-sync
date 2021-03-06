# Git Sync (GitHub ➡️ GitLab)

Backup all GitHub repositories in GitLab.

## Preinstallation

- Create GitHub [access token](https://github.com/settings/tokens/new) with `admin:public_key` and `repo` scope.
- Copy and rename `.env.sample` in the root directory and update it's values.

## Docker Installation

Assuming SSH keys are stored in `~/.ssh` directory.

```
docker build --tag git-sync .
```

## Docker usage

```sh
docker run -it \
    --env-file=".env" \
    -e SSH_PRIVATE_KEY="$(cat ~/.ssh/id_rsa)" \
    -e SSH_PUBLIC_KEY="$(cat ~/.ssh/id_rsa.pub)" \
    -v $PWD/data:/app/data \
    git-sync
```

## Default Installation

```sh
python3 manage.py --install
```

## Default Usage

```sh
python3 index.py
```

## `manage.py` scripts

```sh
python3 manage.py --<flag>
```

| Flag                 | Description                                      |
| -------------------- | ------------------------------------------------ |
| `--install`, `-i`    | Install `pip3`, `yarn`, and `docker` dependecies |
| `--lint`, `-l`       | Lint python files                                |
| `--format`, `-f`     | Format python files                              |
| `--commitlint`, `-c` | Lint commit message                              |
| `--dockerlint`, `-d` | Lint `Dockerfile`                                |
| `--prettier`, `-p`   | Format `json` and `md` file                      |
| `--test`, `-t`       | Run unit tests                                   |
