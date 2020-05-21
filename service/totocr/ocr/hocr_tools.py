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
