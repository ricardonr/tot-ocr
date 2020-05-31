from PIL import Image
from lxml import etree, html
import numpy as np
import ocr.hocr_tools
from PIL import Image
import pytesseract

def OcrTesseract(image,lang='por+eng',config='--psm 1 --oem 1'):


    #Chamada Tesseract
    hocr_bytes = pytesseract.image_to_pdf_or_hocr(image, lang=lang, extension='hocr', config=config)
    hocr_bytes_clean = ocr.hocr_tools.clean_hocr(hocr_bytes)
    return hocr_bytes_clean
