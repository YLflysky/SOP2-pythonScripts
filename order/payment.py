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

    def get_qr_code(self, aid, order_no, channel,score=False):
        '''
        支付底层获取支付二维码API
        :param aid: 用户id
        :param order_no: 订单号
        :param channel: 支付渠道
        :param score: 是否使用积分
        :return:
        '''
        url = self.url + '/pay/qrCode'
        params = {'aid': aid, 'orderNo': order_no, 'payChannel': channel,'useScore':score}
        code, body = self.do_get(url, params)
        self.assert_msg(code, body)
        return body

    def contract_sign_notify(self, aid,service,operator,channel,sign_status,pause_status,**kwargs):
        '''
        支付底层免密签约/解约结果通知接口
        :param aid:用户id
        :param service:FLOW
        :param operator:CMCC
        :param channel:支付渠道
        :param sign_status:签约状态
        :param pause_status:免密开启关闭
        :param kwargs:其他参数
        :return:
        '''
        url = self.url + '/contract/notify/sync_result'
        param = {'serviceId': service, 'aid': aid, 'operatorId': operator, 'payChannel': channel,'signStatus':sign_status,
                 'pauseStatus': pause_status,**kwargs}

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

    def sync_pay_result(self,pay_no,ex_pay_no,pay_time,amount,way,origin,channel,status,**kwargs):
        '''
        支付服务同步支付结果接口
        :param pay_no: 支付编号
        :param ex_pay_no: 外部支付编号,order_pay表中的支付编号
        :param pay_time: 支付时间
        :param amount: 支付金额
        :param way: 支付方式
        :param origin:订单来源
        :param status:支付状态
        :param kwargs:其他参数
        :return:
        '''
        url = self.url + '/pay/notify/payResult/sync'
        data = {'payNo':pay_no,'exPayNo':ex_pay_no,'payTime':pay_time,'payAmount':amount,'payWay':way,
                'origin':origin,'payChannel':channel,'payStatus':status,**kwargs}
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

    def free_qr_code(self, aid, order_no, sp_id, channel):
        '''
        获取签约并支付二维码
        :param sp_id:CMCC
        :param channel:支付渠道ALI_PAY,WECHAT_PAY
        :param aid:用户id
        :return:
        '''

        url = self.url + '/pay/payAndContractQrCode'
        data = {'aid':aid,'orderNo':order_no,'spId':sp_id,'payType':channel}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)

    def free_pay(self,aid,order_no,code):
        '''
        免密支付接口
        :param aid:用户id
        :param order_no:订单号
        :param code:协议码 11101支付宝免密，12101微信免密
        :return:
        '''
        url = self.url + '/contract/pay'
        data = {'aid':aid,'orderNo':order_no,'contractCode':code}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'DEV'
    os.environ['GATE'] = 'false'
    pay = Payment()
    aid = '122'
    # pay.pay_channel(aid='18623459409',order_no='ftb20201203170458721753664')
    # pay.check_route(ex_pay_no='fdb6099683ad4ba6877e65450f9d6e51')
    pay.get_qr_code(aid,order_no='ftb20201203175842120942080',channel='WECHAT_PAY')
    # pay.get_pay_result('20201112111106317868352','221')
    # pay.get_pay_agreement(uid='4614907',order_no='20201012103736463180224',lang='zh-CN',code='11101')
    # pay.ali_pay_callback('trade_success', '2019082466466108', '123456', receipt_amount=57.00, gmt_payment=pay.time_delta(),
    #                      trade_no=pay.f.pyint())
    # pay.contract_sign_notify(aid='221',)
    # pay.sync_pay_result('20201124131211565196608','9409',pay.time_delta(),999,'QR_PAY','BM','ALI_PAY','SUCCESS')
