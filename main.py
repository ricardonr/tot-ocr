from minio import Minio
from rabbitmq_driver import RabbitMqNewWorkloadStream
from minio_driver import MinioNewWorkloadStream, MinioPdfDownloader, MinioOcrUploader, MinioSearchableUploader
from service.tot_ocr import TotOcr

minio_client = Minio(
  'localhost:9000',
  access_key='minioadmin',
  secret_key='minioadmin',
  secure=False
)
minio_new_workload_stream = MinioNewWorkloadStream(minio_client)
rabbitmq_new_workload_stream = RabbitMqNewWorkloadStream('localhost')
pdf_downloader = MinioPdfDownloader(minio_client)
ocr_uploader = MinioOcrUploader(minio_client)
searchable_uploader = MinioSearchableUploader(minio_client)

tot_ocr = TotOcr(
  rabbitmq_new_workload_stream,
  pdf_downloader,
  ocr_uploader,
  searchable_uploader
)
tot_ocr.run()
