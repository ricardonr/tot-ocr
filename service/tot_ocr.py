from .new_workload_stream import NewWorkloadStream
from .pdf_downloader import PdfDownloader
from .ocr_uploader import OcrUploader
from .searchable_uploader import SearchableUploader

from .ocr_service import Ocr
from .searchable_service import Searchable

class TotOcr:

  def __init__(
    self,
    new_workload_stream: NewWorkloadStream,
    pdf_downloader: PdfDownloader,
    ocr_uploader: OcrUploader,
    searchable_uploader: SearchableUploader,
  ):
    self.new_workload_stream = new_workload_stream
    self.pdf_downloader = pdf_downloader
    self.ocr_uploader = ocr_uploader
    self.searchable_uploader = searchable_uploader

    self.ocr = Ocr()
    self.searchable = Searchable()

  def run(self):
    for event in self.new_workload_stream.new_workload('workloads.new'):
      print('EVENT')
      print(event)
      pdf_file = self.pdf_downloader.download_pdf(event.bucket_name, event.object_key)
      ocr_file, hocr_list, image_list = self.ocr.do(pdf_file)
      self.ocr_uploader.upload(ocr_file.split('/')[-1], ocr_file)
      searchable_file = self.searchable.do(pdf_file.split('/')[-1], hocr_list, image_list)
      self.searchable_uploader.upload(searchable_file.split('/')[-1], searchable_file)
      self.ocr.cleanFiles()
