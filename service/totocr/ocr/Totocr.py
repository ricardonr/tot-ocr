from PIL import Image
from lxml import etree, html
import numpy as np
import ocr.hocr_tools
from PIL import Image

def OcrTesseract(image,lang='por+eng',config='--psm 1 --oem 1'):
    import pytesseract

    #Chamada Tesseract
    hocr_bytes = pytesseract.image_to_pdf_or_hocr(image, lang=lang, extension='hocr', config=config)
    return hocr_bytes
