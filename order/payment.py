from box.base import Base

class Payment(Base):
    '''
    底层支付API
    '''
    def __init__(self):
        super().__init__()
        self.url = self.read_conf('sop2_env.conf',self.env,'payment_host')

    def get_pay_result(self,order_no,aid):
        '''
        获取支付结果接口
        '''
        url = self.url + '/pay/qrCodeResult'
        param = {'orderNo':order_no,'aid':aid}
        code,body = self.do_get(url,param)

        self.assert_msg(code,body)
        return body

    def assert_msg(self,code,body):
        print(body)
        assert code == 200

    def get_pay_agreement(self,uid,code,order_no,lang):
        """
        获取支付协议接口
        """
        url = self.url + '/pay/AgreementContent'

        params = {'aid':uid,'agreementCode':code,'orderNo':order_no,'language':lang}
        c,b = self.do_get(url,params)
        self.assert_msg(c,b)
        return b

    def ali_pay_callback(self,trade_status,app_id,out_trade_no,receipt_amount,gmt_payment,trade_no,**kwargs):
        '''
        支付宝支付结果回调，模仿CDP调用该接口
        '''

        url = self.url + '/pay/notify/aliPayQrCallBack'
        data = {'trade_status':trade_status,'app_id':app_id,'out_trade_no':out_trade_no,
                'receipt_amount':receipt_amount,'gmt_payment':gmt_payment,'tradeNo':trade_no,**kwargs}
        code,body = self.do_post(url,data)
        self.assert_msg(code,body)
        return body

    def ger_qr_code(self,aid,order_no,channel):
        '''
        获取支付二维码
        '''
        url = self.url + '/pay/qrCode'
        params = {'aid':aid,'orderNo':order_no,'payChannel':channel}
        code,body = self.do_get(url,params)
        self.assert_msg(code,body)


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'UAT'
    os.environ['GATE'] = 'false'
    pay = Payment()
    # pay.ger_qr_code(aid='9349643',order_no='M202007160901278277176514',channel='ALI_PAY')
    pay.get_pay_agreement(uid='32432',code='12101',order_no='20200907105829249819204',lang='zh-CN')
    # pay.ali_pay_callback('trade_success','2018091361389377','qwer',999,pay.time_delta(),pay.f.pyint())
