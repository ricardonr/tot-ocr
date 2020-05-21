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

def OcrGoogle(image):
   
    import io
    import os
    import google.protobuf.json_format
    import gcv2hocr
    import json
    from google.cloud import vision
    from google.cloud.vision import types

    #Chave privada para acesso aos serviços google cloud plataform
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\Ricardo\\OneDrive - furg.br\\Pesquisa\\ToT\\Programas\\TotOCRGoogle-d8d24f90dfb7.json"

    # Instantiates a client
    client = vision.ImageAnnotatorClient()

    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    content = buffer.getvalue()

    gcv_image = types.Image(content=content)

    # Performs text detection on the image file
    gcv_resp = client.document_text_detection(image=gcv_image)

    #Converte o protobuf para json
    gcv_json = google.protobuf.json_format.MessageToJson(gcv_resp)

    #Converte o json para hocr
    gcv_hocr = gcv2hocr.fromResponse(resp=json.loads(gcv_json)).render()

    gcv_hocr_b = bytes(bytearray(gcv_hocr, encoding='utf-8'))

    return gcv_hocr_b
