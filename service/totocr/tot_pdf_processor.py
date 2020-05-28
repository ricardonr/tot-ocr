# Python imports
from io import BytesIO
import os

# External imports
from lxml import etree
import fitz  #pyMuPdf
from PIL import Image
import numpy

# ToT imports
from ocr.Totocr import OcrTesseract
from ocr.preprocess import preprocess_enaval_form as preprocess
from stamp_detection.signature_extractor import extractSignatures
from ocr.searchable import make_pdfsearchable
import ocr.hocr_tools as hocr_tools
from ocr.hocr_from_searchable import isSearchable, createHocrFromSearchable

class PdfProcessor():
    """ Classe que processa um PDF escaneado"""

    def __init__(self, ocr_lang='por+eng', ocr_config='--psm 1 --oem 1'):
        # Parâmetros:
        self.dpi        = 300                   # resolução da converção de pdf para imagem
        self.ocr_lang   = ocr_lang              # idiomas do ocr
        self.ocr_config = ocr_config            # parâmetros do tesseract ocr

        # Pré-computados:
        self.zoom = fitz.Matrix(self.dpi/72, self.dpi/72)  # amplia amostragem da imagem no fitz (padrão é 72 dpi)

    def process(self, pdf_path, hocr_path = 'document.hocr'):
        """ Extrai as informações do pdf. Salva o hocr em hocr_path. 
        Retorna um JSON com os dados extraidos.
        """

        # Processa cada página independentemente, extraindo informações
        hocr_list = []
        tot_info = '' # JSON com dados extraídos 
        doc = fitz.open(pdf_path)

        for page_i,page in enumerate(doc):
            # Extrai imagem
            pix = page.getPixmap(matrix = self.zoom) # zoom define o dpi usado
            img = Image.open(BytesIO(pix.getImageData()))
            img_np = numpy.array(img)

            # Pré-processamento
            #img_pre = preprocess(img_np)
            img_pre = img_np
            
            # Processa OCR
            if isSearchable(page) is True:
                # Gera hocr a partir de pdf searchable
                hocr = createHocrFromSearchable(page, page_i)
            else:
                # Processa OCR
                hocr = OcrTesseract(img_pre, lang=self.ocr_lang, config=self.ocr_config)
                hocr = hocr_tools.set_page_num(hocr,page_i)

            hocr_list.append(hocr)

            # Pós-processamento

            # Classificador de documentos
            # class = doc_classifier(img_pre, hocr)

            # Extração de tabela

            # Extração de formulário

            # Extração de  assinaturas
            signatures = extractSignatures(img_pre)

            # Extração de carimbos
        
        # Combina as páginas individuais em um único hocr e salva
        hocr_final = hocr_tools.combine_hocr(hocr_list)
        with open(hocr_path,"w+") as f:
            f.write(hocr_final.decode('UTF-8'))
            f.close()

        return tot_info

    def searchable(self,pdf_fname,hocr_fname,output_fname):
        make_pdfsearchable(pdf_fname,hocr_fname,output_fname)

    

# Teste     
if __name__ == "__main__":
    pdf = "/home/laura/Workspace/tot-ocr/test_data/3_page2.pdf" #input
    out = "/home/laura/Workspace/tot-ocr/test_data/3_page2_searchable.pdf" #output
    hocr = "/home/laura/Workspace/tot-ocr/test_data/3_page2.xml" #output
    
    p = PdfProcessor()
    p.process(pdf,hocr)
    p.searchable(pdf,hocr,out)
