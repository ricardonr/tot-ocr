import fitz
import xml.etree.ElementTree as ET
import re
import math

def make_pdfsearchable(pdf_fname,hocr_fname,output_fname,dpi=300):
    """ Adiciona o texto do arquivo hocr sobre o pdf, gerando um novo pdf searchable
    pdf_fname       - Caminho para o arquivo pdf.
    hocr_fname      - Caminho para o arquivo hocr.
    output_fname    - Caminho para o novo arquivo pdf (searchable).
    dpi             - Dots per inch das imagens que geraram hocr
    """

    # Carrega arquivos
    pdf = fitz.open(pdf_fname)  
    hocr = ET.parse(hocr_fname)
    pages = hocr.findall(".//*[@class='ocr_page']")
    #pdf e hocr devem ter o mesmo número de páginas  

    # Expressão regular para extrair bounding box de elementos
    re1 = re.compile(r'(?<=bbox) (?P<left>\d+) (?P<top>\d+) (?P<right>\d+) (?P<botton>\d+)')

    # Itera sobre elementos de texto do hocr
    for page_num,page in enumerate(pages):
        t = page.get('title')
        print(page_num)
        doc_page = pdf.loadPage(page_num)
        words = page.findall(".//*[@class='ocrx_word']")
        for word in words:
            if word.text is not None and word.text != ' ':
                # Extrai a bounding box da palavra
                t = word.get("title")
                bbox = re1.search(t).groupdict()
                box_height = ( float(bbox['botton']) - float(bbox['top']) ) * 72/dpi 
                box_width = ( float(bbox['right']) - float(bbox['left']) ) * 72/dpi  
                
                # Estima fontesize e a matriz para esticar o texto de forma que se enquadre na bbox
                fontsize = math.ceil(box_height*1) # estimado
                text_length = fitz.getTextlength(word.text,fontsize=fontsize) # comprimento do texto
                morph = fitz.Matrix(box_width/text_length,1) # matriz para dar zoom no eixo x do texto

                # Insere o texto na página
                start_point = fitz.Point(float(bbox['left']) * 72/dpi,float(bbox['botton']) * 72/dpi)
                doc_page.insertText(start_point,word.text,render_mode=3,fontsize=fontsize,morph=(start_point,morph)) #render_mode=3 -> invisible
                 
    # Salva o novo pdf
    pdf.save(output_fname)
    pdf.close()

if __name__ == "__main__":
    pdf = "D:\\temp\\tot\\3 - Partículas Magnéticas.pdf"
    hocr = "D:\\temp\\tot\\3 - Partículas Magnéticas.xml"
    out = "D:\\temp\\tot\\3 - Partículas Magnéticas_searchable.pdf"
    make_pdfsearchable(pdf,hocr,out)
