from abc import ABC, abstractmethod

class PdfDownloader(ABC):

  @abstractmethod
  def download_pdf(self, bucket_name: str, object_key: str) -> str:
    pass