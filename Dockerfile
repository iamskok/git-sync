FROM python:slim-buster

ARG ssh_private_key
ARG ssh_public_key

WORKDIR /app

RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y \
    bash \
    git \
    openssh-client

COPY .env main.py requirements.txt ./

RUN pip3 install -r requirements.txt

# Authorize SSH Host
RUN mkdir -p /root/.ssh && \
    chmod 0700 /root/.ssh

# Add the keys and set permissions
RUN echo "$ssh_private_key" > /root/.ssh/id_rsa && \
    echo "$ssh_public_key" > /root/.ssh/id_rsa.pub && \
    chmod 600 /root/.ssh/id_rsa && \
    chmod 600 /root/.ssh/id_rsa.pub

# RUN chmod 400 ~/.ssh/id_rsa
RUN eval "$(ssh-agent -s)" && \
  ssh-add ~/.ssh/id_rsa

CMD ["bash"]
# CMD ["python3", "main.py"]
