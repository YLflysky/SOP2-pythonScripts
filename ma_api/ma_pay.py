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
        self.assert_msg(c,b)

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


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'UAT'
    aid = '4614183'
    vin = 'LMGLS1G53H1003120'
    pay = MAPay(aid=aid,user='15330011918',password='000000',vin='LFVTEST1231231231')
    pay.get_qr_code(aid='4614183',vin=pay.vin,order_no='ma202103191529243291040384',pay_type='11100',category='112')
    # pay.get_pay_channel(vin,aid,order_no='ma20210317111120478856064',category='04')
    # pay.free_pay(vin,order_no='ma20210317111120478856064',code='11101')
    # pay.get_sign_result(aid='4607900',service=27,operator='270001',channel='ALIPAY')
    # pay.get_pay_result(order_no='ma20210317111120478856064',vin=vin,category='04')
