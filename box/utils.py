import yaml

from box.lk_logger import lk
import xml.etree.ElementTree as Etree
from xml.etree.ElementTree import SubElement
from pdfminer.pdfparser import *
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfinterp import PDFResourceManager,PDFPageInterpreter
from pdfminer.layout import *
import os




def add_note(xml_str:str,key,val):
    '''
    xml字符串添加子节点
    :param xml_str: 字符串
    :param key: 子节点键
    :param val: 子节点值
    :return:
    '''
    root = Etree.fromstring(xml_str)
    sub_ele = SubElement(root,key)
    sub_ele.text = val
    return Etree.tostring(root).decode()

def pdf_doc_to_map(pdf_path,password):
    with open(pdf_path,'rb') as obj:
        # 从文件句柄创建一个PDF解析对象
        parser = PDFParser(obj)
        # 创建一个PDF文档对象，储存文档结构
        document = PDFDocument(parser)
        # 创建一个PDF资源管理对象，储存共享资源
        rsrcmcgr = PDFResourceManager(parser)
        laparams = LAParams()
        # 创建一个device对象
        device = PDFPageAggregator(rsrcmcgr,laparams=laparams)
        # 创建一个解释对象
        interpreter = PDFPageInterpreter(rsrcmcgr,device)
        for page in PDFPage.create_pages(document):
            interpreter.process_page(page)
            layout = device.get_result()
            for x in layout:
                if isinstance(x,LTTextBox):
                    lk.prt(x.get_text().strip())
                elif isinstance(x,LTImage):
                    lk.prt("这里获取到一个图片")
                elif isinstance(x,LTFigure):
                    lk.prt('这里获取到一个figure对象')
                elif isinstance(x,LTRect):
                    lk.prt('这里获取到一个矩形')
                elif isinstance(x,LTPage):
                    lk.prt('获取到一个完整的页面或者子对象')
                elif isinstance(x,LTLine):
                    lk.prt('获取到一条直线')
                elif isinstance(x,LTTextLine):
                    lk.prt('获取到单行文本')
                else:
                    lk.prt('不知道是个啥....')

def read_yml(file_path):
    '''

    :param path:
    :return:
    '''
    with open(file_path,'r',encoding='utf-8') as obj:
        data = obj.read()
        return yaml.load(data,Loader=yaml.FullLoader)






if __name__ == '__main__':
    pdf_path = '../data/对账单_DZD20210521163546464675840.pdf'
    pdf_doc_to_map(pdf_path,password=0)
