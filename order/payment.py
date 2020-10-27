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

    def ali_pay_callback(self):
        '''
        支付宝支付结果回调，模仿CDP调用该接口
        '''

        url = self.url + '/pay/notify/aliPayQrCallBack'
        data = {'trade_status':'TRADE_SUCCESS','app_id':'123','out_trade_no':'c7bb647bf47c442a8ae3f6c0dcf4c592',
                'receipt_amount':0}
        code,body = self.do_post(url,data)
        self.assert_msg(code,body)

if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'LOCAL'
    os.environ['GATE'] = 'false'
    pay = Payment()
    pay.ali_pay_callback()
