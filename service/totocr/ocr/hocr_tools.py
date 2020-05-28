from lxml import etree, html


def combine_hocr(hocrs):
#Combina multiplas páginas hocrs individuais em um único hocr 
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

def set_page_num(hocr_str,page_i):
    """ Altera o número da página do hocr"""
    # Corrige os ids com o número da página  
    #hocr = hocr.decode('UTF-8')          
    hocr = hocr_str.replace(b'class=\'ocr_page\' id=\'page_1',
                        b'class=\'ocr_page\' id=\'page_%d' % (page_i))
    hocr = hocr.replace(b'class=\'ocr_carea\' id=\'block_1_',
                        b'class=\'ocr_carea\' id=\'block_%d_' % (page_i))
    hocr = hocr.replace(b'class=\'ocr_par\' id=\'par_1_',
                        b'class=\'ocr_par\' id=\'par_%d_' % (page_i))
    hocr = hocr.replace(b' id=\'line_1_',
                        b' id=\'line_%d_' % (page_i))
    hocr = hocr.replace(b'class=\'ocrx_word\' id=\'word_1_',
                        b'class=\'ocrx_word\' id=\'word_%d_' % (page_i))
    return hocr

def clean_hocr(hocr):
    # Remove palavras inúteis (vazias ou só com espaços)
    
    pages = hocr.findall(".//*[@class='ocr_page']") 
    for page in pages:
        areas = page.findall(".//*[@class='ocr_carea']") 
        for area in areas:
            pars = area.findall(".//*[@class='ocr_par']") 
            for par in pars:
                lines = (par.findall(".//*[@class='ocr_line']") + 
                        par.findall(".//*[@class='ocr_textfloat']") +
                        par.findall(".//*[@class='ocr_caption']") +
                        par.findall(".//*[@class='ocr_header']"))
                for line in lines:
                    words = line.findall(".//*[@class='ocrx_word']")
                    for word in words:
                        # palavra vazia, remove
                        if word.text is None or word.text == ' ' or word.text == '  ' or word.text == '   ' or word.text == '    ' or word.text == '     ': 
                            line.remove(word)
                    if len(line) == 0:
                        par.remove(line)
                if len(par)==0:
                    area.remove(par)
            if len(area)==0:
                page.remove(area)
        if len(page)==0:
            pass # não remove página

    return hocr          
