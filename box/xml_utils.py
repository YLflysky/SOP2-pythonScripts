
import xml.etree.ElementTree as Etree
from xml.etree.ElementTree import SubElement


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

if __name__ == '__main__':
    xml_str = """
        <xml>
            <appid>wx999bec97951ce212</appid>
            <attach>支付测试</attach>
            <bank_type>CMC</bank_type>
            <is_subscribe>Y</is_subscribe>
            <mch_id>1525507701</mch_id>
            <nonce_str>{}</nonce_str>
            <openid>oUpF8uMEb4qRXf22hE3X68TekukE</openid>
            <out_trade_no>{}</out_trade_no>
            <result_code>SUCCESS</result_code>
            <return_code>SUCCESS</return_code>
            <time_end>20201026133500</time_end>
            <total_fee>1</total_fee>
            <cash_fee>0</cash_fee>
            <trade_type>JSAPI</trade_type>
            <transaction_id>1004400740201409030005092168</transaction_id>
        </xml>
    """
    print(add_note(xml_str,'name','sergio'))
