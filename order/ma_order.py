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

    def ma_create_order(self, aid, goods_id, category, vin, quantity,point=False,**kwargs):
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
        data = {'userId':aid,'goodsId': goods_id, 'vin':vin,'orderCategory': category, 'quantity': quantity, 'usedPoint': point, **kwargs}

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

    def sync_order(self,vin,aid,service_id,sp_id,order_type,ex_order,category,title,
                   business_state,desc,amount,discount,pay_amount,business_info,**kwargs):
        '''
        MA提供的外部订单同步结果
        :param vin:
        :param aid:
        :param service_id:
        :param sp_id:
        :param order_type:
        :param ex_order:
        :param category:
        :param title:
        :param business_state:
        :param desc:
        :param amount:
        :param discount:
        :param pay_amount:
        :param business_info:
        :return:
        '''
        url = self.url + '/mosc-order-ma/external/v2/sync/order'
        data = {'vin':vin,'aid':aid,'serviceId':service_id,'spId':sp_id,'orderType':order_type,'exOrderNo':ex_order,
                'orderCategory':category,'title':title,'businessState':business_state,'businessStateDesc':desc,
                'amount':amount,'payAmount':pay_amount,'discountAmount':discount,'businessInfo':business_info,**kwargs}

        c,b = self.do_post(url,data)
        print(b)
        assert c == 200

    def update_status_finish(self,order_no):
        '''
        更改订单状态为FINISHED
        :param order_no:
        :return:
        '''

        url = self.url + '/mosc-order-ma/external/v2/sync/rightsOpen'

        data = {'orderNo':order_no}
        c,b = self.do_post(url,data)
        print(b)
        assert c == 200
        assert b['returnStatus'] == 'SUCCEED'

    def update_business(self,order_no,status,desc):
        '''
        修改订单业务状态API
        :param order_no:订单号
        :param status: 业务状态
        :param desc: 业务状态描述
        :return:
        '''
        url = self.url + '/mosc-order-ma/external/v2/update/businessState'

        data = {'orderNo': order_no,'businessState':status,'businessStateDesc':desc}
        c, b = self.do_post(url, data)
        print(b)
        assert c == 200
        assert b['returnStatus'] == 'SUCCEED'

    def order_detail(self,aid,order_no,vin):
        '''
        MA车机端获取订单详情
        :param aid:
        :param order_no:
        :return:
        '''

        url = self.url + '/mosc-order-ma/order/api/v2/vins/{}/users/{}/orders/{}'.format(vin,aid,order_no)

        c,b = self.do_get(url,None)
        self.assert_bm_msg(c,b)


if __name__ == '__main__':
    from point.points import Points
    import os

    os.environ['ENV'] = 'DEV'
    os.environ['GATE'] = 'false'
    aid = '4614183'
    ma_order = MAOrder(aid,user='15330011918',password='000000',vin='LFVTEST1231231231')
    # ma_order.order_detail(aid,order_no='20210112063038959126976',vin=ma_order.vin)
    # ma_order.update_business(order_no='2020121606064500532768',status='AKSK',desc=ma_order.f.sentence())
    # info = {"poiId":"bd742a558ce01c47","washStoreName":"捌零靓车店"}
    # ma_order.sync_order(vin='B6B3118B019AA7AB0D8BA29E753EDAE1',aid='9349824',service_id='09',sp_id='090002',
    #                     order_type='BUSINESS',ex_order=ma_order.f.md5(),category='09',title='标准洗车-五座轿车',
    #                     business_state='0',desc='待支付',
    #                     amount=35.00,discount=4.10,pay_amount=30.90,timeout=1,
    #                     business_info=info)
    # ma_order.create_h5_order(goods_id='17',category='MUSIC_VIP',count=1,
    #                          usedPoint=True,goodsAmount='19.9',deductionPoint=45,deductionAmount='4.5',actualPayAmount='15.4',
    #                          durationDays=1,vin='LFVTESTMOSC052726')
    # ma_order.get_qr_code('M202012161532571906927437',channel='11100')
    # ma_order.alipay_callback()
    # ma_order.ma_create_order(aid=aid,vin=ma_order.vin,goods_id='17',category='MUSIC_VIP',quantity=1,durationTimes=1,point=False)
    order_no = ma_order.create_order(aid=aid,goods_id='17',category='MUSIC_VIP',quantity=1,point=False,durationTimes=1)['data']
    # order_no = ma_order.create_order(aid=aid,goods_id='32c4785206714d4793d21046a379bd33',category='WIFI_FLOW',quantity=1)['data']
    # ma_order.get_ma_qr_code('20210115103406461180224',pay_type='12100')

    # p = Points()
    # p.get_user_points(aid)
