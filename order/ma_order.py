from box.base import Base

class MAOrder(Base):
    def __init__(self, aid, user, password, vin,tenant='MA',):
        super().__init__(tenant)
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


    def create_h5_order(self, goods_id, vin,category, count, **kwargs):
        '''
        payment-h5创建商品订单
        :param goods_id:
        :param category:
        :param count:
        :param kwargs:
        :return:
        '''
        url = self.payment_url + '/api/v1/createOrder'
        data = {'goodsId': goods_id, 'vin': vin, 'orderCategory': category, 'count': count, **kwargs}
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


    def create_order(self, goods_id, category, aid, quantity, point=False, **kwargs):
        '''
        mosc-order底层创建商品订单接口
        :param goods_id:
        :param category:
        :param aid:
        :param quantity:
        :param point:
        :param kwargs:
        :return:
        '''
        url = self.url + '/mosc-order/internal/v2/goods/creatOrder'
        data = {'aid': aid, 'goodsId': goods_id, 'vin': self.vin,
                'orderCategory': category, 'quantity': quantity, 'usedPoint': point, **kwargs}
        c, b = self.do_post(url, data)
        print(b)
        return b

    def ma_create_order(self, aid,goods_id, category, quantity,point=False,**kwargs):
        '''
        MA车机端创建商品订单接口》》车机端接口
        :param goods_id:商品ID，orderCategory为PAID_CONTENT，priceType为2时，为专辑号，priceType为1时，为音频编号用“,”隔开其他均为商品ID
        :param category:商品类型（MUSIC_VIP，RADIO_VIP，WIFI_FLOW，MEDIA_FLOW，PAID_CONTENT）
        :param price_type:支付方式1音频,2整张专辑orderCategor为PAID_CONTENT，priceType必传
        :param quantity:商品数量
        :param point:是否使用积分抵扣
        :param kwargs:
        :return:
        '''
        url = self.url + '/mos/payment/api/v1/orderCreate'
        data = { 'userId':aid,'goodsId': goods_id, 'vin': self.vin,'orderCategory': category, 'quantity': quantity, 'usedPoint': point, **kwargs}

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

    os.environ['ENV'] = 'DEV'
    os.environ['GATE'] = 'false'
    aid = '4614183'
    ma_order = MAOrder(aid,user='15330011918',password='000000',vin='LFVTEST1231231231')
    # h5_order.get_goods_detail(goods_code=17)
    # ma_order.create_h5_order(goods_id='17',category='MUSIC_VIP',count=1,
    #                          usedPoint=True,goodsAmount='19.9',deductionPoint=45,deductionAmount='4.5',actualPayAmount='15.4',
    #                          durationDays=1,vin='LFVTESTMOSC052726')
    # ma_order.get_qr_code('M202012161532571906927437',channel='11100')
    # ma_order.alipay_callback()
    order_no = ma_order.create_order(aid=aid,goods_id='17',category='MUSIC_VIP',quantity=1,point=True,durationTimes=1)['data']
    # order_no = ma_order.create_order(aid=aid,goods_id='32c4785206714d4793d21046a379bd33',category='WIFI_FLOW',quantity=1)['data']
    # ma_order.get_ma_qr_code('20210106102444716155648',pay_type='12100')

    p = Points()
    p.get_user_points(aid)
