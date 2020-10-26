from box.base import Base

class Payment(Base):
    '''
    底层支付API
    '''
    def __init__(self):
        super().__init__()
        self.url = self.read_conf('sop2_env.conf',self.env,'be_host')

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

        params = {'aid':uid,'agreementCode':code,'order_no':order_no,'language':lang}
        c,b = self.do_get(url,params)
        self.assert_msg(c,b)
        return b


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'LOCAL'
    os.environ['GATE'] = 'false'
    pay = Payment()
    pay.get_pay_agreement(uid='在线',code='11101',order_no='11112223',lang='en-us1')
