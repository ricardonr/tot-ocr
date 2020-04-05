import os
import pdf2image
import pytesseract

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import resolve1
from lxml import etree
from PIL import Image

class Ocr():
    """ Classe que processa um PDF escaneado por um algoritmo de OCR e gera um arquivo XML """
    def __init__(self, batch = 100):
        self.batch = batch
        
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

    def cleanFiles(self):
        """ Limpa arquivos remanescentes. """
        with os.scandir(self.images_path) as files:
            for f in files:
                os.remove(f)

        with os.scandir(self.searchable_path) as files:
            for f in files:
                os.remove(f)

        with os.scandir(self.hocrs_path) as files:
            for f in files:
                os.remove(f)

    def getNumberPages(self, pdf_path: str) -> int:
        """ Obtem o numero de paginas do arquivo pdf """
        f = open(pdf_path, 'rb')
        parser = PDFParser(f)
        document = PDFDocument(parser)
        numPages = resolve1(document.catalog['Pages'])['Count']
        f.close()
        return numPages
    
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

    def processPdf(self, pdf_path: str) -> (list, list):
        """ Extrai, pelo o tesseract, o texto do pdf escaneado """
        hocr_list = []
        images = []
        numPages = self.getNumberPages(pdf_path)
        for initalpage in range(1, numPages+self.batch, self.batch):
            pages = pdf2image.convert_from_path(pdf_path,
                                                first_page=initalpage,
                                                last_page=min(
                                                    initalpage+self.batch-1, numPages),
                                                output_folder=self.images_path,
                                                grayscale='true',
                                                fmt='tif')
            for page in pages:
                hocr_bytes = pytesseract.image_to_pdf_or_hocr(page, 
                                                                lang='por',
                                                                extension='hocr',
                                                                config='--psm 1')
                hocr_list.append(hocr_bytes)
                images.append(page.filename)
                page.close()
        return hocr_list, images

    def do(self, pdf_path: str) -> (str, list, list):
        """ Extrai um arquivo HOCR de um PDF escaneado """
        hocr_list, images = self.processPdf(pdf_path)
        hocr_final = self.combineHocr(hocr_list, pdf_path.split('/')[-1])
        return hocr_final, hocr_list, images
