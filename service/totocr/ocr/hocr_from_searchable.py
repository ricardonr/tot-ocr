import fitz
import json
import sys
import json
import argparse
import math
from string import Template

try:
    from html import escape  # python 3.x
except ImportError:
    from cgi import escape  # python 2.x


class GCVAnnotation:

    templates = {
        'ocr_file': Template("""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="$lang" lang="$lang">
  <head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
    <meta name='ocr-system' content='gcv2hocr.py' />
    <meta name='ocr-number-of-pages' content='1' />
    <meta name='ocr-capabilities' content='ocr_page ocr_carea ocr_line ocrx_word ocrp_lang'/>
  </head>
  <body>
    $content
  </body>
</html>
    """),
        'ocr_page': Template("""
    <div class='ocr_page' id='$htmlid' lang='$lang' title='bbox 0 0 $page_width $page_height'>
        $content
    </div>
    """),
        'ocr_carea': Template("""
        <div class='ocr_carea' id='$htmlid' lang='$lang' title='bbox $x0 $y0 $x1 $y1'>
            $content
        </div>"""),
        'ocr_line': Template("""
            <span class='ocr_line' id='$htmlid' title='bbox $x0 $y0 $x1 $y1; baseline $baseline'>$content
            </span>"""),
        'ocrx_word': Template("""
                <span class='ocrx_word' id='$htmlid' fontsize="$fontsize" title='bbox $x0 $y0 $x1 $y1; x_wconf 100'>$content</span>""")
    }

    def __init__(self,
                 htmlid=None,
                 ocr_class=None,
                 lang='por',
                 baseline="0 -2",
                 page_height=None,
                 page_width=None,
                 content=None,
                 box=None,
                 title='',
                 fontsize=None,
                 savefile=False):
        if content == None:
            self.content = []
        else:
            self.content = content
        self.title = title
        self.htmlid = htmlid
        self.baseline = baseline
        self.page_height = page_height
        self.page_width = page_width
        self.fontsize = fontsize
        self.lang = lang
        self.ocr_class = ocr_class
        self.x0 = box[0]['x'] if 'x' in box[0] and box[0]['x'] > 0 else 0
        self.y0 = box[0]['y'] if 'y' in box[0] and box[0]['y'] > 0 else 0
        self.x1 = box[2]['x'] if 'x' in box[2] and box[2]['x'] > 0 else 0
        self.y1 = box[2]['y'] if 'y' in box[2] and box[2]['y'] > 0 else 0

    def maximize_bbox(self):
        self.x0 = min([w.x0 for w in self.content])
        self.y0 = min([w.y0 for w in self.content])
        self.x1 = max([w.x1 for w in self.content])
        self.y1 = max([w.y1 for w in self.content])

    def __repr__(self):
        return "<%s [%s %s %s %s]>%s</%s>" % (self.ocr_class, self.x0, self.y0,
                                              self.x1, self.y1, self.content,
                                              self.ocr_class)

    def render(self):
        if type(self.content) == type([]):
            content = "".join(map(lambda x: x.render(), self.content))
        else:
            content = escape(self.content)
        return self.__class__.templates[self.ocr_class].substitute(self.__dict__, content=content)

def format_bbox(bbox, landscape, invert, dpi=300):
    if invert is True and landscape is True:
        bbox = [bbox[3], bbox[2]-5, bbox[1], bbox[0]-5]
    bbox = [{"x": math.ceil(bbox[0]/72*dpi), "y": math.ceil(bbox[1]/72*dpi)-8}, {"x": math.ceil(bbox[2]/72*dpi), "y": math.ceil(bbox[3]/72*dpi)-8},
            {"x": math.ceil(bbox[2]/72*dpi), "y": math.ceil(bbox[3]/72*dpi)-8}, {"x": math.ceil(bbox[0]/72*dpi), "y": math.ceil(bbox[1]/72*dpi)-8}]
    return bbox

# Verifica se a página já é searchable
def isSearchable(page):
    dictionary = page.getText('rawdict')
    for block in dictionary['blocks']:
        if block['type'] == 0:
            # Caso exista algum bloco contendo texto, retorna True
            return True
    # Caso não exista nenhum bloco contendo texto, retorna False
    return False

# Verifica se a página está em orientação retrato ou paisagem
def isLandscape(page):
    orientation = page.rotation
    if orientation == 90 or orientation == 270:
        return True
    return False

# Cria hocr a partir de pdf que já é searchable
def createHocrFromSearchable(page, page_count, dpi=300):
    word_count = 1
    line_count = 1
    area_count = 1
    box = [{"x": 0, "y": 0}, {"x": 0, "y": 0},
           {"x": 0, "y": 0}, {"x": 0, "y": 0}]

    landscape = isLandscape(page)

    hocr_doc = GCVAnnotation(
        ocr_class='ocr_file',
        box=box,
        lang='por',
    )
    
    # Extrai o texto da página, utilizando o rawdict
    dictionary = page.getText('rawdict')

    # Extrai as dimensões da página
    dimension = page.bound()

    # Cria uma página
    p = GCVAnnotation(
        ocr_class='ocr_page',
        htmlid='page_%d' % page_count,
        box=box,
        page_width=dimension[2]/72*dpi,
        page_height=dimension[3]/72*dpi
    )

    # Itera por blocos para cada página
    for block in dictionary['blocks']:
        # Verifica se é um bloco que contém texto
        if block['type'] == 0:
            # Gera uma ocr_carea
            area = GCVAnnotation(
                ocr_class='ocr_carea',
                htmlid='block_%d_%d' % (page_count, area_count),
                box=format_bbox(block['bbox'], landscape, True) 
            )
            # Itera para cada linha dentro do bloco em questão
            for line in block['lines']:
                # Gera uma linha
                curline = GCVAnnotation(
                    ocr_class='ocr_line',
                    htmlid='line_%d_%d' % (page_count, line_count),
                    box=format_bbox(line['bbox'], landscape, True)
                )
                # Itera para cada palavra da linha
                for span in line['spans']:
                    w = []
                    string = ''
                    # Itera para cada caracter da linha
                    for char in span['chars']:
                        # Verifica se é o último caracter da palavra,
                        # ou seja, se é um espaço ou o último da linha
                        if char['c'] != ' ' and char != span['chars'][-1]:
                            w.append(char)
                            string += char['c']
                        else:

                            if char == span['chars'][-1] and char['c'] != ' ':
                                w.append(char)
                                string += char['c']
                            if len(w) > 0:
                                if landscape is True:
                                    # Caso seja landscape, é necessário inverter o x e o y
                                    # para que funcione adequadamente
                                    bbox = [w[0]['bbox'][3], w[0]['bbox'][2],
                                        w[len(w)-1]['bbox'][1], w[len(w)-1]['bbox'][0]]
                                else:    
                                    # Caso não seja landscape:
                                    # x0: x0 do primeiro caracter
                                    # y0: y0 do primeiro caracter
                                    # x1: x1 do último caracter
                                    # y1: y1 do último caracter                          
                                    bbox = [w[0]['bbox'][0], w[0]['bbox'][1],
                                        w[len(w)-1]['bbox'][2], w[len(w)-1]['bbox'][3]]
                                # Cria a palavra
                                word = GCVAnnotation(
                                    ocr_class='ocrx_word',
                                    content=string,
                                    box=format_bbox(bbox, landscape, False),
                                    htmlid='word_%d_%d' % (page_count, word_count),
                                    fontsize=span['size'] # Passamos o tamanho da fonte para que o searchable fique melhor
                                )
                                # Adiciona a palavra à linha
                                curline.content.append(word)
                                w = []
                                string = ''
                                word_count += 1
                # Verifica se há algo na linha, caso exista, adiciona à area
                if (len(curline.content) > 0):
                    area.content.append(curline)
                    line_count += 1
            # Adiciona a area à página
            p.content.append(area)
            area_count += 1
    # Maximiza as bounding boxes
    for line in area.content:
        line.maximize_bbox()
    for area in p.content:
        area.maximize_bbox()
    if (len(p.content) > 0):
        p.maximize_bbox()
    # Adiciona a página ao documento
    hocr_doc.content.append(p)
    # Renderiza o arquivo
    hocr = hocr_doc.render()
    hocr = bytes(bytearray(hocr, encoding='utf-8'))
    return hocr



