FROM python:slim-buster

ARG SSH_PRIVATE_KEY
ARG SSH_PUBLIC_KEY

WORKDIR /app

RUN apt-get update -y && \
  apt-get install -y --no-install-recommends \
  git=1:2.20.1-2+deb10u3 \
  openssh-client=1:7.9p1-10+deb10u2 && \
  rm -rf /var/lib/apt/lists/*

COPY index.py requirements.txt ./
COPY src ./src

RUN pip3 install --no-cache-dir -r requirements.txt

RUN mkdir -p ~/.ssh && \
  chmod 0700 ~/.ssh && \
  echo "$SSH_PRIVATE_KEY" > ~/.ssh/id_rsa && \
  echo "$SSH_PUBLIC_KEY" > ~/.ssh/id_rsa.pub && \
  chmod 600 ~/.ssh/id_rsa && \
  chmod 600 ~/.ssh/id_rsa.pub && \
  eval "$(ssh-agent -s)" && \
  ssh-add ~/.ssh/id_rsa

CMD ["python3", "index.py"]
