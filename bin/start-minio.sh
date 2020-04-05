#!/usr/bin/env sh
docker pull minio/minio
docker run \
  -p 9000:9000 \
  minio/minio server /data