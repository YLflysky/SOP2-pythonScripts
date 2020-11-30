from box.base import Base


class BMPayment(Base):
    '''
    BM适配层支付服务API
    '''
    def __init__(self):
        super().__init__()
        self.hu_url = self.read_conf('sop2_env.conf',self.env,'hu_host')
        self.be_url = self.read_conf('sop2_env.conf',self.env,'be_host')

    def get_qr_code(self,vin,aid,order_no,pay_type,category):
        '''
        BM车机端获取支付二维码
        '''

        url = self.hu_url + '/payment/api/v2/vins/{}/users/{}/orders/{}/payments/qrCode'.format(vin,aid,order_no)

        data = {'payType':pay_type,'orderCategory':category}
        c,b = self.do_get(url,data)
        print(b)
        return b

    def get_pay_agreement(self,aid,order_no,code,language):
        '''
        BM适配层获取支付协议
        '''
        url = self.hu_url + '/payment/api/v2/orders/{}/payments/AgreementContent'.format(order_no)
        self.header['aid'] = aid
        data = {'language':language,'agreementCode':code}
        c,b = self.do_get(url,data)
        print(b)
        return b

    def get_pay_result(self,vin,order_no,aid,category,roll_number):
        '''
        BM适配层获取支付结果
        '''
        url = self.hu_url + '/payment/api/v2/vins/{}/orders/{}/payments/qrCodeResult'.format(vin,order_no)
        self.header['aid'] = aid
        data = {'orderCategory':category,'rollNumber':roll_number}
        c,b = self.do_get(url,data)
        print(b)
        return b

    def get_pay_channel(self,vin,aid,order_no,category):
        '''
        BM车机端获取支付渠道
        :return:
        '''
        url = self.hu_url + '/payment/api/v2/vins/{}/users/{}/orders/{}/payments/payChannel'.format(vin,aid,order_no)
        data = {'orderCategory':category}
        c,b = self.do_get(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':
    import os
    from order.oder_api import Order
    os.environ['ENV']='UAT'
    os.environ['GATE']='false'
    order = Order()

    pay = BMPayment()
    # pay.get_pay_result(vin='123',order_no='orderNo0001',aid='00',category='102',roll_number=1)
    # pay.get_pay_channel(vin='6WU7LOB55T2R5E5PL',aid='9642113',order_no='111124424523',category='107')
    # pay.get_pay_agreement(aid='221',order_no='20201029154015868266240',language=None,code='12101')
    pay.get_qr_code(vin='123',aid='32432',order_no='20200907105829249819204',pay_type='11100',category='110')
