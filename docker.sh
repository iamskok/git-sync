#!/bin/bash
NAME=iamskok/git-sync

docker build --tag $NAME:$1 \
             --tag $NAME:latest .

docker push $NAME:$1
docker push $NAME:latest
