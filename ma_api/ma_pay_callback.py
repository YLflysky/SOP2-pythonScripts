from box.base import Base
import xmltodict
from box import utils
import json
import hashlib


class MAPayCallback(Base):
    '''
    mosc-pay回调&系统内部调用接口
    '''
    def __init__(self):
        super().__init__()
        self.gate = True
        self.be_url = self.read_conf('ma_env.conf', self.env, 'base_url_back') + '/mosc-payment'
        self.h5_url = self.read_conf('ma_env.conf', self.env, 'base_url_back') + '/mos/payment'

    def ma_contract_sign(self,channel,service,operator,aid,vin):
        '''
        MA免密签约api
        :param channel:签约渠道WXPAY,ALPAY
        :param service: 业务，目前支持GAS,03
        :param operator: CP，目前支持JDO,030003
        :return:
        '''
        url = self.be_url + '/internal/v2/app/contract/sign'
        data = {'aid':aid,'operatorId':operator,'payChannel':channel,'serviceId':service,'vin':vin}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)
        return b

    def close_sign(self,aid,service,operator,channel,vin):
        '''
        关闭免密签约
        :param aid:
        :return:
        '''
        url = self.be_url + '/internal/v2/contract/pause'
        data = {'aid': aid, 'operatorId': operator, 'payChannel': channel, 'serviceId': service, 'vin': vin}
        c, b = self.do_post(url, data)
        self.assert_bm_msg(c, b)
        return b

    def open_sign(self,aid,service,operator,channel,vin):
        '''
        开启免密签约
        :param aid:
        :return:
        '''
        url = self.be_url + '/internal/v2/contract/open'
        data = {'aid': aid, 'operatorId': operator, 'payChannel': channel, 'serviceId': service, 'vin': vin}
        c, b = self.do_post(url, data)
        self.assert_bm_msg(c, b)
        return b

    def sync_pay(self,aid,orderNo,channel,pay_type,payAmount,payTime,pay_status,**kwargs):
        '''

        :return:
        '''
        url = self.be_url + '/external/v2/sync/pay'
        data = {'aid':aid,'orderNo':orderNo,'payChannel':channel,'payType':pay_type,'payAmount':payAmount,
                'payTime':payTime,'payStatus':pay_status,**kwargs
                }
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)

    def jdo_sign_sync(self,ali,wechat,user):
        '''
        JDO免密签约回调
        :param ali:
        :param wechat:
        :param user:
        :return:
        '''
        url = self.be_url + '/external/v2/sync/contract/jdo/api/autoPay'
        data = {'enableAutoPayAli':ali,'enableAutoPayWechat':wechat,'userId':user}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)

    def ali_pay_callback(self,out_trade_no, receipt_amount, gmt_payment, trade_no, **kwargs):
        '''

        :param out_trade_no:
        :param receipt_amount:
        :param gmt_payment:
        :param trade_no:
        :param kwargs:
        :return:
        '''
        url = self.be_url + '/internal/v2/alipayQrCallBack'
        data = {'trade_status': 'trade_success', 'app_id': '2018091361389377', 'out_trade_no': out_trade_no,
                'receipt_amount': receipt_amount, 'gmt_payment': gmt_payment, 'trade_no': trade_no, **kwargs}
        code, body = self.do_post(url, data)
        self.assert_bm_msg(code, body)
        return body

    def wechat_callback(self,out_trade_no,nonce,pay_amount):
        url = self.be_url + '/internal/v2/weixinQrCallBack'
        time_stmp = self.time_delta(formatted='%Y%m%d%H%M%S')
        data = """
        <xml>
            <appid>1wx999bec97951ce212</appid>
            <attach>支付测试</attach>
            <bank_type>CMC</bank_type>
            <is_subscribe>Y</is_subscribe>
            <mch_id>11525507701</mch_id>
            <nonce_str>{}</nonce_str>
            <openid>oUpF8uMEb4qRXf22hE3X68TekukE</openid>
            <out_trade_no>{}</out_trade_no>
            <result_code>SUCCESS</result_code>
            <return_code>SUCCESS</return_code>
            <time_end>{}</time_end>
            <total_fee>{}</total_fee>
            <cash_fee>0</cash_fee>
            <trade_type>JSAPI</trade_type>
            <transaction_id>1004400740201409030005092168</transaction_id>
        </xml>
        """.format(nonce,out_trade_no,time_stmp,pay_amount)
        self.header['Content-type'] = 'application/xml; charset=utf-8'
        data_sign = self.xml_to_json(data)['xml']
        sign = self.weixin_sign('abcd1234abcd1234abcd1234abcd1234',data_sign)
        data = utils.add_note(data, 'sign', sign)

        c,b = self.do_post(url,data)
        self.assert_msg(c,b)


    def weixin_sign(self,sign_key,data_str:dict):
        keys_list = list(data_str.keys())
        keys_list.sort(key=None, reverse=False)
        string_a = ''
        for dict_key in keys_list:
            string_a = string_a + dict_key + '=' + data_str.get(dict_key) + '&'
        string_a = string_a.rstrip('&')
        print(string_a)
        string_sign_temp = string_a + "&key=" + sign_key
        print('stringSignTemp:' + string_sign_temp)
        sign_MD5 = hashlib.md5(string_sign_temp.encode("UTF-8")).hexdigest().upper()
        print("sign_MD5=", sign_MD5)
        return sign_MD5

    def xml_to_json(self,xml_str):
        '''
        xml字符串转为字典
        :param xml_str:
        :return:
        '''

        xml_parse = xmltodict.parse(xml_str)
        json_str = json.dumps(xml_parse,indent=1)
        print(json_str)
        return json.loads(json_str)

    def app_pay_info(self,aid,order_no,pay_type):
        url = self.be_url + '/internal/v2/payments/payInfo'
        data = {'userId':aid,"orderNo":order_no,'payType':pay_type}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def get_sign_result(self,aid,service,operator,channel):
        '''
        外部接口获取免密签约状态
        :param aid:
        :param services:
        :param channel:
        :return:
        '''

        url = self.be_url + '/external/v2/contract/query'
        services = [{'serviceId':service,'operatorId':operator}]
        data = {'aid':aid,'services':services,'payChannel':channel}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)

    def h5_find_order_by_temp(self,temp_id):
        url = self.h5_url + '/mos/internal/findOrderNoByOrderTempNo'
        data = {'tempOrderId':temp_id}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'UAT'
    aid = '9349824'
    vin = 'LFV3A23C913046742'
    pay = MAPayCallback()
    # pay.h5_find_order_by_temp(temp_id='32c300611dc44d05a78a2c4f1f1a39d2')
    # pay.app_pay_info(aid='4614233',order_no='ma20210422180915944778240',pay_type='12100')
    # pay.ali_pay_callback(out_trade_no='68202ee127154b01919f8cca44f877af', buyer_logon_id='995939534@qq.com',
    #                      receipt_amount=0.01, gmt_payment=pay.time_delta(), trade_no=pay.f.pyint())
    # pay.wechat_callback(out_trade_no='fc2c47a42ca849fe98ba133185d71c6c', nonce=pay.f.md5(), pay_amount=16350)
    # pay.jdo_sign_sync(ali=0,wechat=0,user='10086')
    # pay.sync_pay(aid='9349641',orderNo='ma20210413112322974778240',channel='WECHAT_PAY',discountAmount=2.00,
    #              pay_type='QR_CODE',payAmount=1.00,payTime=pay.get_time_stamp(),pay_status='SUCCESS')
    # pay.close_sign(aid='4607236',service='03',operator='030001',channel='ALIPAY',vin='LFVSOP2TEST000407')
    pay.get_sign_result(aid='4607236',service='03',operator='030003',channel='ALIPAY')
    # pay.sign_and_pay_result(vin='LFVSOP2TEST000043',order_no='ma20210413095545831774144',roll_number=1)
    # pay.get_pay_result(order_no='ma20210413095545831774144',vin=vin,category='04')
