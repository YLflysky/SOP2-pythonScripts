from box.base import Base


class BMPayment(Base):
    '''
    BM适配层支付服务API
    '''
    def __init__(self):
        super().__init__()
        self.hu_url = self.read_conf('sop2_env.conf',self.env,'hu_host')
        self.be_url = self.read_conf('sop2_env.conf',self.env,'be_host')

    def get_qr_code(self,vin,aid,order_no,pay_type,category,score=None):
        '''
        BM车机端获取支付二维码
        :param vin: 车辆vin
        :param aid: 大众用户id
        :param order_no: 订单号
        :param pay_type: 支付方式11100支付宝12100微信11103支付宝支付并签约12103微信支付并签约
        :param category:订单类型
        :param score:是否使用积分Y使用N不使用
        :return:
        '''

        url = self.hu_url + '/payment/api/v2/vins/{}/users/{}/orders/{}/payments/qrCode'.format(vin,aid,order_no)

        data = {'payType':pay_type,'orderCategory':category,'useScore':score}
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
        self.assert_bm_msg(c,b)
        return b

    def get_agreement_qr_code(self,aid,vin,channel,service_id,sp_id):
        '''
        BM车机端获取免密签约二维码
        :param aid:用户id
        :param channel:支付渠道 1=支付宝 2=微信
        :param service_id:服务id
        :param sp_id:供应商id
        :return:
        '''
        url = self.hu_url + '/payment/api/v1/vins/{}/users/{}/payments/agreementSignqr'.format(vin,aid)
        self.header['serviceId'] = service_id
        data = {'operatorId':sp_id,'payType':channel}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def free_pay(self,aid,vin,order_no,useScore=False):
        '''
        BM车机端免密支付接口
        :param aid:大众用户id
        :param vin:车辆vin码
        :param order_no:订单号
        :return:
        '''
        url = self.hu_url + '/order/api/v2/vins/{}/users/{}/orders/{}/payments/withholdPayment'.format(aid,vin,order_no)
        data = {'userScore':useScore}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)


if __name__ == '__main__':
    import os
    from order.order_api import Order
    os.environ['ENV']='DEV'
    os.environ['GATE']='false'
    order = Order()
    pay = BMPayment()
    aid = '9351499'
    vin = 'SO8OY5T6JXM7B76O6'
    # pay.get_pay_result(vin='123',order_no='orderNo0001',aid='00',category='102',roll_number=1)
    # pay.get_pay_channel(vin,aid=aid,order_no='ftb20201204113739602753664',category='111')
    # pay.get_pay_agreement(aid='221',order_no='20201029154015868266240',language=None,code='12101')
    pay.get_qr_code(vin,aid,order_no='ftb20201210105333938753664',pay_type='11103',category='111')
    # pay.get_agreement_qr_code(aid,vin,channel=2,service_id='FLOW',sp_id='CMCC')
