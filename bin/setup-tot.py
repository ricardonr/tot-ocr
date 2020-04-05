#!/usr/bin/env python3
import argparse

from minio import Minio
from minio.error import BucketAlreadyOwnedByYou, BucketAlreadyExists, ResponseError

parser = argparse.ArgumentParser(description="Uploads a file to Minio Object Storage")
parser.add_argument('--host', dest='minio_host', default='localhost:9000', help='Minio host address without schema (default: localhost:9000)')
parser.add_argument('--credentials', default='minioadmin:minioadmin', help='Access and secret keys pair (default: minioadmin:minioadmin)')
parser.add_argument('--secure', type=bool, default=False, help='Wether to connect with HTTPS or not (default: False)')
args = parser.parse_args()

[access_key, secret_key] = args.credentials.split(':')
minio_client = Minio(
  args.minio_host,
  access_key=access_key,
  secret_key=secret_key,
  secure=args.secure
)

tot_buckets = [ 'tot-pdf', 'tot-ocr', 'tot-searchable' ]
for bucket in tot_buckets:
  try:
    minio_client.make_bucket(bucket)
  except BucketAlreadyOwnedByYou as err:
    pass
  except BucketAlreadyExists as err:
    pass
  except ResponseError as err:
    raise
  else:
    print('created', bucket, 'bucket')