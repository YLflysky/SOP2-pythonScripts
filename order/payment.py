from box.base import Base


class Payment(Base):
    '''
    底层支付API
    '''

    def __init__(self):
        super().__init__()
        self.url = self.read_conf('sop2_env.conf', self.env, 'payment_host')
        self.second_url = self.read_conf('sop2_env.conf', self.env, '2nd_host')

    def get_pay_result(self, order_no, aid):
        '''
        获取支付结果接口
        '''
        url = self.url + '/pay/qrCodeResult'
        param = {'orderNo': order_no, 'aid': aid}
        code, body = self.do_get(url, param)

        self.assert_msg(code, body)
        return body

    def assert_msg(self, code, body):
        print(body)
        assert code == 200

    def get_pay_agreement(self, uid, code, order_no, lang):
        """
        获取支付协议接口
        """
        url = self.url + '/pay/agreementContent'

        params = {'aid': uid, 'agreementCode': code, 'orderNo': order_no, 'language': lang}
        c, b = self.do_get(url, params)
        self.assert_msg(c, b)
        return b

    def ali_pay_callback(self, trade_status, app_id, out_trade_no, receipt_amount, gmt_payment, trade_no, **kwargs):
        '''
        支付宝支付结果回调，模仿CDP调用该接口
        '''

        url = self.second_url + '/pay/notify/v1/aliPayQrCallBack'
        data = {'trade_status': trade_status, 'app_id': app_id, 'out_trade_no': out_trade_no,
                'receipt_amount': receipt_amount, 'gmt_payment': gmt_payment, 'trade_no': trade_no, **kwargs}
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)
        return body

    def get_qr_code(self, aid, order_no, channel):
        '''
        获取支付二维码
        '''
        url = self.url + '/pay/qrCode'
        params = {'aid': aid, 'orderNo': order_no, 'payChannel': channel}
        code, body = self.do_get(url, params)
        self.assert_msg(code, body)
        return body

    def cmcc_callback(self, aid, enterprise, channel, notify_type, status):
        '''
        免密支付结果回调接口
        '''
        url = self.url + '/contract/notify/cmcc'
        param = {'enterpriseId': enterprise, 'userId': aid, 'channel': channel, 'notifyType': notify_type,
                 'contractStatus': status}

        code, body = self.do_post(url, param)
        self.assert_msg(code, body)
        return body

    def sync_pay_stream(self, data):
        '''
        同步支付记录接口
        '''
        url = self.url + '/pay/notify/payOrder/sync'
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)
        return body

    def check_route(self,ex_pay_no):
        '''
        检查是否为FTB的支付流水
        :param ex_pay_no:支付流水号
        :return:
        '''
        url = self.url + '/pay/checkRoute'
        data = {'payNo':ex_pay_no}
        code,body = self.do_get(url,data)
        self.assert_msg(code,body)
        return body

    def sync_pay_result(self,pay_no,ex_pay_no,pay_time,amount,way,origin,channel,**kwargs):
        '''
        支付服务同步支付结果接口
        :param pay_no: 支付编号
        :param ex_pay_no: 外部支付编号,order_pay表中的支付编号
        :param pay_time: 支付时间
        :param amount: 支付金额
        :param way: 支付方式
        :param origin:订单来源
        :param kwargs:其他参数
        :return:
        '''
        url = self.url + '/pay/notify/payResult/sync'
        data = {'payNo':pay_no,'exPayNo':ex_pay_no,'payTime':pay_time,'payAmount':amount,'payWay':way,
                'origin':origin,'payChannel':channel,**kwargs}
        code,body = self.do_post(url,data)
        self.assert_msg(code,body)
        return body

    def pay_channel(self,aid,order_no):
        '''
        获取支付协议
        :param aid:用户id
        :param order_no:订单编号
        :return:
        '''
        url = self.url + '/pay/payChannel'
        params = {'aid':aid,'orderNo':order_no}
        c,b = self.do_get(url,params)
        self.assert_msg(c,b)


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'DEV'
    os.environ['GATE'] = 'false'
    pay = Payment()
    # pay.pay_channel(aid='9642113',order_no='111124424523')
    # pay.check_route(ex_pay_no='fdb6099683ad4ba6877e65450f9d6e51')
    # pay.get_qr_code(aid='9642113',order_no='orderNo0001',channel='ALI_PAY')
    # pay.get_pay_result('20200907105829249819204','32432')
    # pay.get_pay_agreement(uid='4614907',order_no='20201012103736463180224',lang='zh-CN',code='11101')
    # pay.ali_pay_callback('trade_success', '2018091361389377', '135ad3ff2d0c42edb1acf22a64111eb9', 999, pay.time_delta(),
    #                      pay.f.pyint())
    pay.cmcc_callback(aid='221',enterprise='2100010000',channel=1,notify_type=2,status=1)
    # pay.sync_pay_result('135ad3ff2d0c42edb1acf22a64111eb9','9409',pay.time_delta(),999,'QR_PAY','BM','ALI_PAY')
