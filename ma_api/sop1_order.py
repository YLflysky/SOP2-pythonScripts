from ma_api.ma_order import MABase

class SOP1Order(MABase):
    def __init__(self, aid, user, password, vin):
        super().__init__(aid, user, password, vin)
        self.payment_url = self.read_conf('ma_env.conf', self.env, 'payment_h5_host')
        self.url = self.read_conf('ma_env.conf', self.env, 'hu_host')
        self.mobile_url = self.read_conf('ma_env.conf', self.env, 'one_app_host')

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
        url = self.payment_url + '/api/v1/orderCreate'
        data = {'userId':aid,'goodsId': goods_id, 'vin':vin,'orderCategory': category, 'count': quantity, 'usedPoint': point, **kwargs}

        c, b = self.do_post(url, data)
        print(b)
        return b

    def sop1_calendar_sync(self):
        url = self.mobile_url + '/mos/calendar/public/event/sync'
        event= [{'localEventId': self.f.pyint(100, 1000), 'cudStatus': 'C','rrule':'Only Once',
                     'eventStartTime': self.get_time_stamp(days=-1), 'eventEndTime': self.get_time_stamp(days=1)}]
        data = {'currentTime': self.time_delta(), 'events': event}
        c, b = self.do_post(url, data, gateway='APP')
        self.assert_bm_msg(c,b)


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'CLOUD'
    aid = '4614233'
    vin = 'LFV2A2BUXL4651255'
    sop1 = SOP1Order(aid,user='15144142651',password='Qq111111',vin=vin)
    # sop1.sop1_calendar_sync()
    sop1.sop1_create_order(aid=aid,vin=vin,goods_id='8a248c5a231b4e2d99ec8183b578e339',category='MEDIA_FLOW',quantity=1,point=False)
