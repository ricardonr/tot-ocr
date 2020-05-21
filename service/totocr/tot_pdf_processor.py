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

        for page_i,page in enumerate(doc):
            # Extrai imagem
            pix = page.getPixmap(matrix = self.zoom) # zoom define o dpi usado
            img = Image.open(BytesIO(pix.getImageData()))
            img_np = numpy.array(img)

            # Pré-processamento
            img_pre = preprocess(img_np)
            
            # Processa OCR
            hocr = OcrTesseract(img_pre, lang=self.ocr_lang, config=self.ocr_config)
            # Corrige os ids com o número da página  
            #hocr = hocr.decode('UTF-8')          
            hocr = hocr.replace(b'class=\'ocr_page\' id=\'page_1',
                                b'class=\'ocr_page\' id=\'page_%d' % (page_i))
            hocr = hocr.replace(b'class=\'ocr_carea\' id=\'block_1_',
                                b'class=\'ocr_carea\' id=\'block_%d_' % (page_i))
            hocr = hocr.replace(b'class=\'ocr_par\' id=\'par_1_',
                                b'class=\'ocr_par\' id=\'par_%d_' % (page_i))
            hocr = hocr.replace(b' id=\'line_1_',
                                b' id=\'line_%d_' % (page_i))
            hocr = hocr.replace(b'class=\'ocrx_word\' id=\'word_1_',
                                b'class=\'ocrx_word\' id=\'word_%d_' % (page_i))
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
        hocr_str = etree.tostring(doc, pretty_print=True)

        return hocr_str

# Teste     
if __name__ == "__main__":
    pdf = "./test_data/tot_enaval_test.pdf" #input
    hocr = "./test_data/tot_enaval_test.xml" #output
    out = "./test_data/tot_enaval_test_searchable.pdf" #output
    
    p = PdfProcessor()
    p.process(pdf,hocr)
    p.searchable(pdf,hocr,out)
