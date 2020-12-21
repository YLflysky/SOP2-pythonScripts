from box.base import Base


class H5Order(Base):
    def __init__(self):
        super().__init__()
        self.env = 'UAT'
        self.gate = True
        self.vin = 'LFVTESTMOSC000096'
        self.url = self.read_conf('ma_env.conf', self.env, 'payment_h5_host')
        self.add_header(url=self.read_conf('ma_env.conf',self.env,'token_host'),
                        user='15843013681', password='aa123456', vin=self.vin)

    def assert_msg(self, code, body):
        print(body)
        assert 200 == code
        assert body['status'] == 'SUCCEED'

    def create_order(self,goods_id,category,count,**kwargs):
        url = self.url + '/api/v1/createOrder'
        data = {'goodsId':goods_id,'vin':self.vin,'orderCategory':category,'count':count,**kwargs}
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)

    def get_qr_code(self, order_no,channel):
        url = self.url + '/api/v1/getQRCodeImage'
        data = {
            "vin": "LFV2A11KXA3030241",
            "orderNo": order_no,
            "payType": channel
        }
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)

    def get_goods_list(self):
        url = self.url + ''

    def alipay_callback(self):
        url = self.url + 'mos/internal/alipayQrCallBack'
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


class MAOrder(H5Order):
    def __init__(self):
        super().__init__()
        self.env = 'UAT'
        self.gate = True
        self.vin = 'LFVTESTMOSC000096'
        self.url = self.read_conf('ma_env.conf', self.env, 'mosc_order')
        self.add_header(url=self.read_conf('ma_env.conf',self.env,'token_host'),
                        user='15843013681', password='aa123456', vin=self.vin)

    def create_ma_order(self, goods_id, category, aid,quantity,point=False, **kwargs):
        url = self.url + '/internal/v2/goods/creatOrder'
        data = {'aid':aid,'goodsId': goods_id, 'vin': self.vin, 'durationTimes':1,
                'orderCategory': category, 'quantity': quantity,'usedPoint':point, **kwargs}
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)
        return b

    def get_goods_list(self):
        url = self.url + '/internal/v2/goods/list'



if __name__ == '__main__':
    # h5_order = H5Order()
    # h5_order.create_order(goods_id='32c4785206714d4793d21046a379bd33',category='WIFI_FLOW',count=1,)
    # ma_order.get_qr_code('M202012161532571906927437',channel='11100')
    # ma_order.alipay_callback()
    aid = '914'
    ma_order = MAOrder()
    order_no = ma_order.create_ma_order(aid=aid,goods_id='17',category='MUSIC_VIP',quantity=1,)['order_no']
    # ma_order.get_qr_code(order_no,channel='11100')
