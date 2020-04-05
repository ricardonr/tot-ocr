from service import NewWorkloadEvent, NewWorkloadStream, PdfDownloader, OcrUploader, SearchableUploader
from minio import Minio
from typing import Iterator

class MinioNewWorkloadStream(NewWorkloadStream):

  def __init__(self, minio_client: Minio):
    self.minio_client = minio_client

  def new_workload(self, bucket_name: str) -> Iterator[NewWorkloadEvent]:
    return self.__new_pdf_event_generator(bucket_name)

  def __new_pdf_event_generator(self, bucket_name: str):
    events = self.minio_client.listen_bucket_notification(
      bucket_name,
      events=[
        's3:ObjectCreated:*'
      ]
    )
    for event in events:
      for record in event['Records']:
        bucket_name: str = record['s3']['bucket']['name']
        object_key: str = record['s3']['object']['key']
        yield NewWorkloadEvent(object_key, bucket_name, object_key)

class MinioPdfDownloader(PdfDownloader):

  def __init__(self, minio_client: Minio):
    self.minio_client = minio_client

  def download_pdf(self, bucket_name: str, object_key: str) -> str:
    pdf_file: str = './' + object_key
    self.minio_client.fget_object(bucket_name, object_key, pdf_file)
    return pdf_file

class MinioOcrUploader(OcrUploader):

  def __init__(self, minio_client: Minio):
    self.minio_client = minio_client

  def upload(self, object_key: str, ocr_file: str):
    self.minio_client.fput_object('tot-ocr', object_key, ocr_file)

class MinioSearchableUploader(SearchableUploader):

  def __init__(self, minio_client: Minio):
    self.minio_client = minio_client

  def upload(self, object_key: str, searchable_file: str):
    self.minio_client.fput_object('tot-searchable', object_key, searchable_file)