from abc import ABC, abstractmethod
from typing import Iterator

class NewWorkloadEvent:

  def __init__(
    self,
    id: str,
    bucket_name: str,
    object_key: str,
  ):
    self.id = id
    self.bucket_name = bucket_name
    self.object_key = object_key

class NewWorkloadStream(ABC):

  @abstractmethod
  def new_workload(self, topic: str) -> Iterator[NewWorkloadEvent]:
    pass