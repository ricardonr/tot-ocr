from abc import ABC, abstractmethod

class OcrUploader(ABC):

  @abstractmethod
  def upload(self, object_key: str, file: str):
    pass