# Python imports
from io import BytesIO
from lxml import etree
import os

# External imports
import pdf2image
import pytesseract
import fitz
from PIL import Image

# ToT imports
from ocr.Totocr import OcrTesseract
from ocr.preprocess import preprocess_enaval_form as preprocess
from stamp_detection.signature_extractor import extractSignatures
from ocr.searchable import make_pdfsearchable

class PdfProcessor():
    """ Classe que processa um PDF escaneado"""

    def __init__(self, ocr_lang='por+eng', ocr_config='--psm 1 --oem 1'):
        # Parâmetros:
        self.dpi        = 300                   # resolução da converção de pdf para imagem
        self.ocr_lang   = ocr_lang              # idiomas do ocr
        self.ocr_config = ocr_config            # parâmetros do tesseract ocr

        # Pré-computados:
        self.zoom = fitz.Matrix(self.dpi/72, self.dpi/72)  # amplia amostragem da imagem no fitz (padrão é 72 dpi)

    def searchable(self,pdf_fname,hocr_fname,output_fname):
        make_pdfsearchable(pdf_fname,hocr_fname,output_fname)

    def process(self, pdf_path, hocr_path = 'document.hocr'):
        """ Extrai as informações do pdf. Salva o hocr em hocr_path. 
        Retorna um JSON com os dados extraidos.
        """

        # Processa cada página independentemente, extraindo informações
        hocr_list = []
        tot_info = '' # JSON com dados extraídos 
        doc = fitz.open(pdf_path)

        for page,page_i in enumerate(doc):
            # Extrai imagem
            pix = page.getPixmap(matrix = self.zoom) # zoom define o dpi usado
            img = Image.open(BytesIO(pix.getImageData()))

            # Pré-processamento
            img_pre = preprocess(img)
            
            # Processa OCR
            hocr = OcrTesseract(img_pre, lang=self.ocr_lang, config=self.ocr_config, page_num=page_i)
            hocr_list.append(hocr)

            # Pós-processamento

            # Classificador de documentos
            # class = doc_classifier(img_pre, hocr)

            # Extração de tabela

            # Extração de formulário

            # Extração de  assinaturas
            # signatures = extractSignatures(img_pre)

            # Extração de carimbos
        
        # Combina as páginas individuais em um único hocr
        hocr_final = self.combineHocr(hocr_list)
        with open(hocr_path,"w+") as f:
            f.write(hocr_final.decode('UTF-8'))
            f.close()

        return tot_info

    def combineHocr(self, hocrs: list):
        """ Combina multiplas páginas hocrs individuais em um único hocr """
        doc=etree.fromstring(hocrs[0])
        pages = doc.xpath("//*[@class='ocr_page']")
        container = pages[-1].getparent()

        for hocr in hocrs[1:]:
            doc2 = etree.fromstring(hocr)
            pages = doc2.xpath("//*[@class='ocr_page']")
            for page in pages:
                container.append(page)

        return doc
         
