# Python imports
from io import BytesIO
from lxml import etree
import os

# External imports
import pdf2image
import pytesseract
import fitz as PyMuPdf
from PIL import Image

# ToT imports
from ocr.Totocr import OcrTesseract
from ocr.preprocess import preprocess_enaval_form as preprocess
from stamp_detection.signature_extractor import extractSignatures

class DocUnderstanding():
    """ Classe que processa um PDF escaneado"""

    def __init__(self, dpi = 300):
        # Parâmetros:
        self.dpi        = 300   # resolução da converção de pdf para imagem
        
        # TODO: mudar para tempdir (pois pode dar problema com execuções em paralelo) 
        files_path = os.getcwd() + "/files" 
        if not os.path.isdir(files_path):
            os.mkdir(files_path)
        
        self.images_path = files_path + "/images/"
        if not os.path.isdir(self.images_path):
            os.mkdir(self.images_path)

        self.hocrs_path = files_path + "/hocrs/"
        if not os.path.isdir(self.hocrs_path):
            os.mkdir(self.hocrs_path)

        self.searchable_path = files_path + "/searchable/"
        if not os.path.isdir(self.searchable_path):
            os.mkdir(self.searchable_path)

        # Pré-computados:
        self.zoom = fitz.Matrix(dpi/72, dpi/72)  # amplia tamanho de imagem do fitz (original tem 72 dpi)

    def processPdf(self, pdf_path: str) -> (list, list):
        """ Extrai o texto do pdf escaneado """

        # Extrai hocr de cada página
        hocr_list = []
        doc = PyMuPdf.open(pdf_path) 
        for page,page_i in enumerate(doc):
            # Extrai imagem
            pix = page.getPixmap(matrix = self.zoom) # zoom define o dpi usado
            img = Image.open(BytesIO(pix.getImageData()))

            # Pré-processamento
            img_pre = preprocess(img)
            
            # Processa OCR
            hocr = OcrTesseract(img_pre, lang='por+eng', config='--psm 1 --oem 1', page_num=page_i)
            hocr_list.append(hocr)

            # Pós-processamento

            # Classificador de documentos
            # class = doc_classifier(img, hocr_bytes)

            # Extração de tabela

            # Extração de formulário

            # Extração de  assinaturas
            signatures = extractSignatures(img_pre)

            #
        
        # Combina as páginas individuais em um único hocr
        hocr_final = self.combineHocr(hocr_list, pdf_path.split('/')[-1])
        return hocr_final

    def combineHocr(self, hocrs: list, name: str) -> str:
        """ Combina multiplas páginas hocrs individuais em um único hocr """
        doc=etree.fromstring(hocrs[0])
        pages = doc.xpath("//*[@class='ocr_page']")
        container = pages[-1].getparent()

        for hocr in hocrs[1:]:
            doc2 = etree.fromstring(hocr)
            pages = doc2.xpath("//*[@class='ocr_page']")
            for page in pages:
                container.append(page)

        hocr_str = etree.tostring(doc, pretty_print=True)

        hocr_path = self.hocrs_path + name
        f = open(hocr_path, 'w+')
        f.write(hocr_str.decode("UTF-8"))
        f.close
        return hocr_path

    def do(self, pdf_path: str) -> (str, list, list):
        """ Extrai um arquivo HOCR de um PDF escaneado """
        hocr_list, images = self.processPdf(pdf_path)
        hocr_final = self.combineHocr(hocr_list, pdf_path.split('/')[-1])
        return hocr_final, hocr_list, images
