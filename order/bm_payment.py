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

    def free_pay(self,aid,vin,order_no,channel,useScore=False):
        '''
        BM车机端免密支付接口
        :param aid:大众用户id
        :param vin:车辆vin码
        :param order_no:订单号
        :return:
        '''
        url = self.hu_url + '/payment/order/api/v2/vins/{}/users/{}/orders/{}/payments/withholdPayment'.format(vin,aid,order_no)
        data = {'agreementProductCode':channel,'useScore':useScore}
        c,b = self.do_put(url,data)
        self.assert_bm_msg(c,b)

    def be_sync_result(self,vin,aid,bm_order_no,bm_pay_no,order_no,pay_amount,
                       order_amount,channel,status,pay_time,pay_way,service,sp,**kwargs):
        '''
        BM后台同步支付记录API
        :param vin: 车架号
        :param aid: 一汽大众账号id
        :param bm_order_no: BM订单号
        :param bm_pay_no: BM支付流水号
        :param order_no: 一汽大众订单号
        :param pay_amount: 支付金额（分）
        :param order_amount: 订单金额（分）
        :param channel: 支付渠道 ALI_PAY,WECHAT_PAY
        :param status: 支付状态 INIT,WAIT_BUYER_PAY,TRADE_SUCCESS,TRADE_CLOSED,TRADE_FINISHED,TRADE_FAILED
        :param pay_time: 订单支付时间（yyyy-MM-dd HH:mm:ss）
        :param pay_way:支付方式 FREE_PASS_PAY QR_PAY
        :param service:
        :param sp:
        :param kwargs:
        :return:
        '''
        url = self.be_url + '/payment/api/v1/pay_order/sync'
        data = {'vin':vin,'userId':aid,'bmOrderNo':bm_order_no,'bmPayNo':bm_pay_no,'orderNo':order_no,'payAmount':pay_amount,
                'orderAmount':order_amount,'payChannel':channel,'payStatus':status,'payTime':pay_time,'payWay':pay_way,
                'serviceId':service,'spId':sp,**kwargs}

        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)


if __name__ == '__main__':
    import os
    from order.order_api import Order
    os.environ['ENV'] = 'UAT'
    os.environ['GATE'] = 'false'
    order = Order()
    pay = BMPayment()
    aid = '9353490'
    vin = 'LFV1A23C6L3309793'
    order_no='ftb20210322172742594970752'
    # pay.be_sync_result(vin='5E5F5EDBD91F4BF8462AE2DE2E89B509',aid='9349485',bm_order_no='bm001',bm_pay_no='bm_pay_001',order_no='ftb20210115135413613139264',pay_amount=1,order_amount=100,discountAmount=99,
    #                    channel='WECHAT_PAY',status='TRADE_SUCCESS',pay_time=pay.time_delta(),pay_way='QR_PAY',service='GAS',sp='111')
    # pay.get_pay_result(vin='LFVTESTMOSC989216',order_no='ftb20210113104218446114688',aid='9351484',category='112',roll_number=1)
    # pay.get_pay_channel(vin=vin,aid=aid,order_no=order_no,category='111')
    # pay.get_pay_agreement(aid='221',order_no='20201029154015868266240',language='en-US',code='11101')
    pay.get_qr_code(vin,aid=aid,order_no=order_no,pay_type='12100',category='109',score='N')
    # pay.get_agreement_qr_code(aid,vin,channel=2,service_id='FLOW',sp_id='CMCC')
