# Gerenciadores de arquivos
from .new_workload_stream import NewWorkloadStream
from .pdf_downloader import PdfDownloader
from .ocr_uploader import OcrUploader
from .searchable_uploader import SearchableUploader

# Processadores do pdf
from .ocr_service import Ocr
from .searchable_service import Searchable

class TotDocUnderstandingService:
  """ Serviço que processa documentos pdf do ToT e extrai:
  - Texto (OCR)
  - Tabelas
  - Formulários
  - Carimbos e assinaturas
  - Outras informações sobre o documento
  """

  def __init__(
    self,
    new_workload_stream: NewWorkloadStream,
    pdf_downloader: PdfDownloader,
    ocr_uploader: OcrUploader,
    searchable_uploader: SearchableUploader,

  ):
    # Gerenciadores de arquivos
    self.new_workload_stream = new_workload_stream
    self.pdf_downloader = pdf_downloader
    self.ocr_uploader = ocr_uploader
    self.searchable_uploader = searchable_uploader

    # Processadores do documento
    self.ocr = Ocr()
    self.searchable = Searchable()

  def run(self):
    """ Executa o serviço de processamento dos pdfs. Escuta evento de novos pdfs e os processa."""

    for event in self.new_workload_stream.new_workload('workloads.new'):
      # Baixa o pdf
      print('EVENT')
      print(event)
      pdf_file = self.pdf_downloader.download_pdf(event.bucket_name, event.object_key)

      # Processa
      hocr_file = self.ocr.do(pdf_file)
      self.ocr_uploader.upload(hocr_file.split('/')[-1], hocr_file)

      searchable_file = self.searchable.do(pdf_file.split('/')[-1], hocr_list, image_list)
      self.searchable_uploader.upload(searchable_file.split('/')[-1], searchable_file)

      # Limpa arquivos temporários
      self.ocr.cleanFiles()
