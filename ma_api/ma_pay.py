from ma_api.ma_order import MABase


class MAPay(MABase):
    def __init__(self, aid, user, password, vin, token=True):
        super().__init__(aid, user, password, vin, token)

        self.payment_url = self.read_conf('ma_env.conf', self.env, 'pay_host')

    def get_sign_result(self,aid,service,operator,channel):
        '''
        外部接口获取免密签约状态
        :param aid:
        :param services:
        :param channel:
        :return:
        '''

        url = self.payment_url + '/external/v2/contract/query'
        services = [{'serviceId':service,'operatorId':operator}]
        data = {'aid':aid,'services':services,'payChannel':channel}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)

    def get_pay_result(self,order_no,vin,category):
        '''
        车机端支付结果查询
        :param order_no:
        :param vin:
        :param category:
        :return:
        '''
        url = self.payment_url + '/api/v2/vins/{}/orders/{}/payments/qrCodeResult'.format(vin,order_no)
        data = {'orderCategory':category}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def sign_and_pay_result(self,vin,order_no,roll_number):
        '''
        轮询接口，签约结果和
        :param vin:
        :param order_no:
        :param roll_number:
        :return:
        '''
        url = self.payment_url + '/api/v2/vins/{}/orders/{}/payments/signAndPayResult'.format(vin,order_no)
        data = {'rollNumber':roll_number}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def free_pay(self,vin,order_no,code):
        '''
        车机端免密支付接口
        :param vin:
        :param order_no:
        :param code:11101支付宝免密，12101微信免密
        :return:
        '''
        url = self.payment_url + '/api/v2/vins/{}/orders/{}/payments/withholdPayment'.format(vin,order_no)
        data = {'agreementProductCode':code}
        c,b = self.do_put(url,data)
        self.assert_bm_msg(c,b)

    def get_pay_channel(self, vin,aid,order_no,category):
        '''
        MA获取支付方式
        :param aid: 用户id
        :param vin: 车架号
        :param order_no: 订单号
        :param category: 订单category
        :return:
        '''
        url = self.payment_url + '/api/v2/vins/{}/users/{}/orders/{}/payments/payChannel'.format(vin, aid,order_no)

        data = {'orderCategory': category}
        c, b = self.do_get(url, data)
        self.assert_bm_msg(c,b)

    def get_qr_code(self, vin,aid,order_no, pay_type,category):
        '''
        MOSC-PAY 获取支付二维码
        :param order_no: 订单号
        :param pay_type: 支付方式11100,11103,12100,12103
        :return:
        '''
        url = self.payment_url + '/api/v2/vins/{}/users/{}/orders/{}/payments/qrCode'.format(vin,aid,order_no)
        data = {
            "orderCategory": category,
            "payType": pay_type
        }
        c, b = self.do_get(url, data)
        self.assert_bm_msg(c, b)

    def ma_contract_sign(self,channel,service,operator):
        '''
        MA免密签约api
        :param channel:签约渠道WXPAY,ALPAY
        :param service: 业务，目前支持GAS,03
        :param operator: CP，目前支持JDO,030003
        :return:
        '''
        url = self.payment_url + '/internal/v2/app/contract/sign'
        data = {'aid':self.aid,'operatorId':operator,'payChannel':channel,'serviceId':service,'vin':self.vin}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)
        return b

    def close_sign(self,aid,service,operator,channel,vin):
        '''
        关闭免密签约
        :param aid:
        :return:
        '''
        url = self.payment_url + '/internal/v2/contract/pause'
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
        url = self.payment_url + '/internal/v2/contract/open'
        data = {'aid': aid, 'operatorId': operator, 'payChannel': channel, 'serviceId': service, 'vin': vin}
        c, b = self.do_post(url, data)
        self.assert_bm_msg(c, b)
        return b

    def get_sign_qr_code(self,vin,aid,service,shop,sign_type,order_no):
        '''
        车机端获取免密签约二维码
        :param vin:
        :param aid:
        :param service:
        :param shop:
        :param sign_type:
        :param order_no:
        :return:
        '''
        url = self.payment_url + '/internal/v2/sync/pay'
        pass

    def sync_pay(self,aid,orderNo,channel,pay_type,payAmount,payTime,pay_status,**kwargs):
        '''

        :return:
        '''
        url = self.payment_url + '/external/v2/sync/pay'
        data = {'aid':aid,'orderNo':orderNo,'payChannel':channel,'payType':pay_type,'payAmount':payAmount,
                'payTime':payTime,'payStatus':pay_status,**kwargs
                }
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)

    def get_goods_detail(self, goods_code):
        url = self.payment_url + '/api/v2/shelvesProducts/{}/detail'.format(goods_code)
        c, b = self.do_get(url, None)
        assert c == 200
        print(b)

if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'UAT'
    aid = '9349824'
    vin = 'LFV3A23C913046742'
    pay = MAPay(aid=aid,user='18217539032',password='Abc123456',vin=vin,token=True)
    pay.sync_pay(aid='9349641',orderNo='ma20210413112322974778240',channel='WECHAT_PAY',discountAmount=2.00,
                 pay_type='QR_CODE',payAmount=1.00,payTime=pay.get_time_stamp(),pay_status='SUCCESS')
    # pay.get_qr_code(aid=aid,vin=vin,order_no='ma20210413142713102774144',pay_type='11100',category='112')
    # pay.get_pay_channel(vin='LFVSOP2TEST000050',aid='9349832',order_no='ma20210412145453968479232',category='04')
    # pay.free_pay(vin,order_no='ma20210412145453968479232',code='11101')
    # pay.close_sign(aid='9349485',service='27',operator='270001',channel='WECHAT_PAY',vin='LFVSOP2TEST000407')
    # pay.get_sign_result(aid='9349832',service='27',operator='270001',channel='ALIPAY')
    # pay.sign_and_pay_result(vin='LFVSOP2TEST000043',order_no='ma20210413095545831774144',roll_number=1)
    # pay.get_pay_result(order_no='ma20210413095545831774144',vin=vin,category='04')
