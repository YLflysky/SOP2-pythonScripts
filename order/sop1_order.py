from box.base import Base

class SOP1Order(Base):
    def __init__(self, aid, user, password, vin,tenant='SOP1',):
        super().__init__(tenant)
        self.env = 'UAT'
        self.gate = True
        self.vin = vin
        self.aid = aid
        self.payment_url = self.read_conf('ma_env.conf', self.env, 'payment_h5_host')
        self.url = self.read_conf('ma_env.conf', self.env, 'hu_host')
        self.add_header(url=self.read_conf('ma_env.conf', self.env, 'token_host'),
                        user=user, password=password, vin=vin)

    def sop1_create_order(self, aid, goods_id, category, vin, quantity,point=False,**kwargs):
        '''
        SOP1车机端创建商品订单接口》》车机端接口
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

if __name__ == '__main__':
    aid = '4614183'
    sop1 = SOP1Order(aid,user='15330011918',password='000000',vin='LFVTEST1231231231')
