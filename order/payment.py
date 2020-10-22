from box.base import Base

class Payment(Base):
    '''
    底层支付API
    '''
    def __init__(self):
        super().__init__()
        self.url = self.read_conf('sop2_env.conf',self.env,'host')


    def get_pay_result(self,order_no,aid):

        url = self.url + '/pay/qrCodeResult'
        param = {'orderNo':order_no,'aid':aid}
        code,body = self.do_get(url,param)

        self.assert_msg(code,body)
        return body

    def assert_msg(self,code,body):
        assert code == 200
        print(body)


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'LOCAL'
    os.environ['GATE'] = 'false'
    pay = Payment()
    pay.get_pay_result(order_no='20200907105829249819205',aid='32432')
