import os
import zlib
import base64
import io
import re

from PIL import Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.ttfonts import TTFont
from lxml import etree

class Searchable():
    """ Classe que implementa a geração de um PDF Searchable """
    def __init__(self, batch = 100):
        files_path = os.getcwd() + "/files"
        if not os.path.isdir(files_path):
            os.mkdir(files_path)

        self.images_path = files_path + "/images/"
        if not os.path.isdir(self.images_path):
            os.mkdir(self.images_path)
        
        self.searchable_path = files_path + "/searchable/"
        if not os.path.isdir(self.searchable_path):
            os.mkdir(self.searchable_path)
        
        self.font = """eJzdlk1sG0UUx/+zs3btNEmrUKpCPxikSqRS4jpfFURUagmkEQQoiRXgAl07Y3vL2mvt2ml8APXGhQPiUEGEVDhWVHyIC1REPSAhBOWA+BCgSoULUqsKcWhVBKjhzfPU+VCi3Flrdn7vzZv33ryZ3TUEgC6chsTx8fHck1ONd98D0jnS7jn26GPjyMIleZhk9fT0wcHFl1/9GRDPkTxTqHg1dMkzJH9CbbTkxbWlJfKEdB+Np0pBswi+nH/Nvay92VtfJp4nvEztUJkUHXsdksUOkveXK/X5FNuLD838ICx4dv4NI1e8+ZqbxwCNP2jyqXoV/fmhy+WW/2SqFsb1pX68SfEpZ/TCrI3aHzcP//jitodvYmvL+6Xcr5mVvb1ScCzRnPRPfz+LsRSWNasuwRrZlh1sx0E8AriddyzEDfE6EkglFhJDJO5u9fJbFJ0etEMB78D54Djm/7kjT0wqhSNURyS+u/2MGJKRu+0ExNkrt1pJti9p2x6b3TBJgmUXuzgnDmI8UWMbkVxeinCwMo311/l/v3rF7+01D+OkZYE0PrbsYAu+sSyxU0jLLtIiYzmBrFiwnCT9FcsdOOK8ZHbFleSn0znPnDCnxbnAnGT9JeYtrP+FOcV8nTlNnsoc3bBAD85adtCNRcsSffjBsoseca/lBE7Q09LiJOm/ttyB0+IqcwfncJt5q4krO5k7jV7uY+5m7mPebuLKUea7iHvk48w72OYF5rvZT8C8k/WvMN/Dc19j3s02bzPvZZv3me9j/ox5P9t/xdzPzPVJcc7yGnPL/1+GO1lPVTXM+VNWOTRRg0YRHgrUK5yj1kvaEA1ExAWiCtl4qJL2ADKkG6Q3XxYjzEcR0E9hCj5KtBd1xCxp6jV5mKP7LJBr1nTRK2h1TvU2w0akCmGl5lWbBzJqMJsdyaijQaCm/FK5HqspHetoTtMsn4LO0T2mlqcwmlTVOT/28wGhCVKiNANKLiJRlxqBF603axQznIzRhDSq6EWZ4UUs+xud0VHsh1U1kMlmNwu9kTuFaRqpURU0VS3PVmZ0iE7gct0MG/8+2fmUvKlfRLYmisd1w8pk1LSu1XUlryM1MNTH9epTftWv+16gIh1oL9abJZyjrfF5a4qccp3oFAczWxxx4DpvlaKKxuytRDzeth5rW4W8qBFesvEX8RFRmLBHoB+TpCmRVCCb1gFCruzHqhhW6+qUF6tCpL26nlWN2K+W1LhRjxlVGKmRTFYVo7CiJug09E+GJb+QocMCPMWBK1wvEOfRFF2U0klK8CppqqvGpylRc2Zn+XDQWZIL8iO5KC9S+1RekOex1uOyZGR/w/Hf1lhzqVfFsxE39B/ws7Rm3N3nDrhPuMfcw3R/aE28KsfY2J+RPNp+j+KaOoCey4h+Dd48b9O5G0v2K7j0AM6s+5WQ/E0wVoK+pA6/3bup7bJfCMGjwvxTsr74/f/F95m3TH9x8o0/TU//N+7/D/ScVcA=""".encode('latin1')
        uncompressed = bytearray(zlib.decompress(base64.b64decode(self.font)))
        ttf = io.BytesIO(uncompressed)
        setattr(ttf, "name", "(invisible.ttf)")
        pdfmetrics.registerFont(TTFont('invisible', ttf))     
    
    def do(self, name: str, hocr_list: list, images: list) -> str:
        """ Cria um pdf searchable combinando imagens com hocr """
        pdf_path = self.searchable_path + name + "_searchable.pdf"
        pdf = Canvas(pdf_path)
        pdf.setCreator('TotOcr')
        pdf.setTitle(name)
        dpi = 300

        p1 = re.compile(r'bbox((\s+\d+){4})')
        p2 = re.compile(r'baseline((\s+[\d\.\-]+){2})')
        for img_path, hocr in zip(images, hocr_list):
            img = Image.open(img_path)
            w, h = img.size
            width = w * 72 / dpi
            height = h * 72 / dpi
            pdf.setPageSize((width, height))
            pdf.drawImage(img_path, 0, 0, width=width, height=height)
            hocr_et=etree.fromstring(hocr)
            img.close()

            #Draw a text layer for OCR data
            for line in hocr_et.xpath('//*[@class="ocr_line"]'):
                linebox = p1.search(line.attrib['title']).group(1).split()
                try:
                    baseline = p2.search(line.attrib['title']).group(1).split()
                except AttributeError:
                    baseline = [0, 0]
                linebox = [float(i) for i in linebox]
                baseline = [float(i) for i in baseline]
                xpath_elements = './/*[@class="ocrx_word"]'
                if (not (line.xpath('boolean(' + xpath_elements + ')'))):
                    # if there are no words elements present,
                    # we switch to lines as elements
                    xpath_elements = '.'
                for word in line.xpath(xpath_elements):
                    rawtext = word.text.strip()
                    if rawtext == '':
                        continue
                    font_width = pdf.stringWidth(rawtext, 'invisible', 8)
                    if font_width <= 0:
                        continue
                    box = p1.search(word.attrib['title']).group(1).split()
                    box = [float(i) for i in box]
                    b = (((box[0] + box[2]) / 2 - linebox[0])*baseline[0] + baseline[1]) + linebox[3]
                    text = pdf.beginText()
                    text.setTextRenderMode(3)  # double invisible
                    text.setFont('invisible', 8)
                    text.setTextOrigin(box[0] * 72 / dpi, height - b * 72 / dpi)
                    box_width = (box[2] - box[0]) * 72 / dpi
                    text.setHorizScale(100.0 * box_width / font_width)
                    text.textLine(rawtext)
                    pdf.drawText(text)
            pdf.showPage()
        pdf.save()
        return pdf_path
