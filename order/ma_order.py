from box.base import Base


class MAOrder(Base):
    def __init__(self, aid, user, password, vin):
        super().__init__()
        self.env = 'UAT'
        self.gate = True
        self.vin = vin
        self.aid = aid
        self.payment_url = self.read_conf('ma_env.conf', self.env, 'payment_h5_host')
        self.url = self.read_conf('ma_env.conf', self.env, 'hu_host')
        self.add_header(url=self.read_conf('ma_env.conf', self.env, 'token_host'),
                        user=user, password=password, vin=vin)

    def assert_msg(self, code, body):
        print(body)
        assert 200 == code
        assert body['status'] == 'SUCCEED'

    def create_order(self, goods_id, category, count, **kwargs):
        url = self.payment_url + '/api/v1/createOrder'
        data = {'goodsId': goods_id, 'vin': self.vin, 'orderCategory': category, 'count': count, **kwargs}
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)

    def get_qr_code(self, order_no, channel):
        url = self.payment_url + '/api/v1/getQRCodeImage'
        data = {
            "vin": "LFV2A11KXA3030241",
            "orderNo": order_no,
            "payType": channel
        }
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)

    def get_goods_detail(self, goods_code):
        url = self.payment_url + '/api/v2/shelvesProducts/{}/detail'.format(goods_code)
        c, b = self.do_get(url, None)
        assert c == 200
        print(b)

    def get_goods_list(self):
        pass

    def alipay_callback(self):
        url = self.payment_url + 'mos/internal/alipayQrCallBack'
        data = {"gmt_create": "2020-04-28 14:32:45",
                "charset": "utf-8",
                "seller_email": "wenbowang@pateo.com.cn",
                "subject": "立即上架时间",
                "buyer_id": "2088402022287119",
                "invoice_amount": "0.40",
                "notify_id": "2020042800222143251087110514730802",
                "fund_bill_list": "[{amount:0.40,fundChannel:ALIPAYACCOUNT}]",
                "notify_type": "trade_status_sync",
                "trade_status": "TRADE_SUCCESS",
                "receipt_amount": "0.40",
                "buyer_pay_amount": "0.40",
                "app_id": "2018061260355242",
                "seller_id": "2088631104404692",
                "gmt_payment": "2020-04-28 14:32:50",
                "notify_time": "2020-04-28 14:32:51",
                "version": "1.0",
                "out_trade_no": "M202004281809133265701539",
                "total_amount": "0.40",
                "trade_no": "2020042822001487110593127602",
                "auth_app_id": "2019082466466108",
                "buyer_logon_id": "642***@qq.com",
                "point_amount": "0.00"}
        c, b = self.do_post(url, data)
        print(b)
        assert 200 == c

    def create_ma_order(self, goods_id, category, aid, quantity, point=False, **kwargs):
        url = self.url + '/mosc-order/internal/v2/goods/creatOrder'
        data = {'aid': aid, 'goodsId': goods_id, 'vin': self.vin, 'durationTimes': 1,
                'orderCategory': category, 'quantity': quantity, 'usedPoint': point, **kwargs}
        c, b = self.do_post(url, data)
        print(b)
        return b

    def get_ma_qr_code(self, order_no, pay_type):
        '''
        MA订单获取支付二维码
        :param aid: 用户id
        :param order_no: 订单号
        :param pay_type: 支付类型11100支付宝普通支付11103支付宝支付并签约
        :return:
        '''
        url = self.url + '/mosc-payment/api/v2/vins/{}/users/{}/orders/{}/payments/qrCode'.format(self.vin, self.aid,
                                                                                                  order_no)
        data = {'payType': pay_type}
        c, b = self.do_get(url, data)
        print(b)
        assert c == 200


if __name__ == '__main__':
    from point.points import Points
    import os

    os.environ['ENV'] = 'UAT'
    os.environ['GATE'] = 'false'
    user_info = {'aid': '4614183', 'user': '', 'password': '', 'vin': ''}
    ma_order = MAOrder()
    # h5_order.get_goods_detail(goods_code=17)
    # h5_order.create_order(goods_id='32c4785206714d4793d21046a379bd33',category='WIFI_FLOW',count=1,)
    # ma_order.get_qr_code('M202012161532571906927437',channel='11100')
    # ma_order.alipay_callback()
    # order_no = ma_order.create_ma_order(aid=aid,goods_id='17',category='MUSIC_VIP',quantity=1,point=False)['data']
    # ma_order.get_ma_qr_code(aid,'20201222150230007778240',pay_type='11100')

    p = Points()
    p.get_user_points(aid)
