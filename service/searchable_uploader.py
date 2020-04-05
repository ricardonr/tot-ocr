from abc import ABC,  abstractmethod

class SearchableUploader(ABC):

  @abstractmethod
  def upload(self, object_key: str, searchable_file: str):
    pass