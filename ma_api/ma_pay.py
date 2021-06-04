from ma_api.ma_order import MABase


class MAPay(MABase):
    def __init__(self, aid, user, password, vin, token=True):
        super().__init__(aid, user, password, vin, token)

        self.payment_url = self.read_conf('ma_env.conf', self.env, 'pay_host')
        self.be_url = self.read_conf('ma_env.conf', self.env, 'pay_be_host')

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

    def sign_and_pay_result(self,vin,order_no,roll_number):
        '''
        轮询接口，签约结果和
        :param vin:
        :param order_no:
        :param roll_number:
        :return:
        '''
        url = self.payment_url + '/api/v2/vins/{}/orders/{}/payments/signAndPayResult'.format(vin,order_no)
        data = {'rollNumber':roll_number}
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


    def get_goods_detail(self, goods_code):
        url = self.payment_url + '/api/v2/shelvesProducts/{}/detail'.format(goods_code)
        c, b = self.do_get(url, None)
        assert c == 200
        print(b)

    def app_pay_info(self,aid,order_no,pay_type):
        url = self.payment_url + '/internal/v2/payments/payInfo'
        data = {'userId':aid,"orderNo":order_no,'payType':pay_type}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)



if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'PROD'
    aid = '4614183'
    vin = 'LFVTEST1231231231'
    # pay = MAPay(aid=aid,user='15330011918',password='000000',vin=vin)
    pay = MAPay(aid='15867227',user='13618079403',password='xyz2020',vin='LFVSOP2TESTLY0040')
    # pay.app_pay_info(aid='4614233',order_no='ma20210425133535414774144',pay_type='11100')

    pay.get_qr_code(aid='15867227',vin='LFVSOP2TESTLY0040',order_no='ma20210603160336695794624',pay_type='11100',category='112')
    # pay.get_pay_channel(vin='LFVSOP2TEST000050',aid='9349832',order_no='ma20210412145453968479232',category='04')
    # pay.free_pay(vin,order_no='ma20210419093418222774144',code='11101')
    # pay.sign_and_pay_result(vin='LFVSOP2TEST000043',order_no='ma20210413095545831774144',roll_number=1)
    # pay.get_pay_result(order_no='ma20210413095545831774144',vin=vin,category='04')
