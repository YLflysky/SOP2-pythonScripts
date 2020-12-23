from box.base import Base


class BMOrder(Base):
    '''
    BM适配层订单服务API
    '''

    def __init__(self):
        super().__init__()
        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
        self.be_url = self.read_conf('sop2_env.conf', self.env, 'be_host')

    def order_count(self, vin, uid, **kwargs):
        '''
        according to the order status,time returns the order quantity
        '''

        url = self.hu_url + '/order/api/v2/vins/{}/orders/count'.format(vin)
        self.header['aid'] = uid
        params = {**kwargs}
        code, body = self.do_get(url, params)
        print(body)
        return body

    def reload_config(self):
        '''
        重新加载category配置接口
        '''
        url = self.hu_url + '/order/api/v2/order/map/reload'
        code, body = self.do_get(url, None)
        self.assert_bm_msg(code, body)

    def sync_bm_order(self, bm_order_id, data):
        '''
        订单适配层同步BM订单
        '''
        url = self.be_url + '/order/api/v2/orders/{}/sync'.format(bm_order_id)

        code, body = self.do_post(url, data)
        self.assert_bm_msg(code, body)
        return body

    def update_bm_order(self, order_no, vin, userId, updateType, **kwargs):
        '''
        BM适配层更新订单
        '''
        url = self.be_url + '/order/api/v2/orders/{}/status'.format(order_no)
        params = {'vin': vin, 'userId': userId, 'updateType': updateType, **kwargs}
        code, body = self.do_put(url,params)
        self.assert_bm_msg(code, body)

    def bm_order_detail(self, aid, order_no, vin, token=None):
        '''
        BM车机端获取订单详情接口
        '''
        url = self.hu_url + '/order/api/v2/vins/{}/users/{}/orders/{}'.format(vin, aid, order_no)
        if aid:
            self.header['aid'] = aid
        else:
            self.header['Authorization'] = token
        code, body = self.do_get(url, None)
        self.assert_bm_msg(code, body)
        return body

    def music_order_create(self, tenant_id, aid, vin, goods, quantity):
        '''
        EP后台创建音乐订单接口
        :param tenant_id: FTB2.2
        :param aid: 大众用户id
        :param vin: 车辆vin吗
        :param goods: 商品id
        :param quantity: 商品数量
        :return:
        '''
        url = self.hu_url + '/order/api/v1/orderCreate'
        self.header['tenantId'] = tenant_id
        data = {'userId': aid, 'vin': vin, 'goodsId': goods, 'quantity': quantity}
        c, b = self.do_post(url, data)
        print(b)
        return b

    def bm_cancel_order(self,aid,order_no):
        '''
        BM车机端取消订单
        :param aid: 大众用户Id
        :param order_no:订单号
        :return:
        '''
        url = self.hu_url + '/order/api/v1/orders/{}/cancel'.format(order_no)
        self.header['aid'] = aid
        token_url = self.read_conf('sop2_env.conf',self.env,'token_host')
        self.header['Authorization'] = self.get_token(token_url,username='19900001143',password='000000',vin='H6LZ8FUH6U662V48S')
        c,b = self.do_put(url,None)
        self.assert_bm_msg(c,b)


if __name__ == '__main__':
    import os

    os.environ['ENV'] = 'UAT'
    os.environ['GATE'] = 'false'
    o = BMOrder()
    aid = '4614907'
    vin = 'BMTESTZ9AUOGCF4KK'
    # o.order_count(vin=123,uid='469317')
    data = {"brand": "VW", "businessExtInfo": {"message": "\u6269\u5c55\u5b57\u6bb5\u6d4b\u8bd5"},
            "createdTime": "1601346979941", "discountAmount": "2000", "orderAmount": "20000", "orderCategory": "99",
            "serviceId": "serviceId002", "serviceOrderState": "serviceOrderState002",
            "serviceOrderStateDesc": "serviceOrderStateDesc002", "spId": "spId002", "title": "title_test002",
            "userId": "U002", "vin": "5E5F5EDBD91F4BF8462AE2DE2E89B509"}
    # o.sync_bm_order(o.f.md5(), data)
    # o.bm_cancel_order(aid='4614931',order_no='ftb20201203160039247753664')
    # o.order_count(vin='DEFAULT_VIN',uid='33')
    # o.update_bm_order(order_no='20201104154521856385024',vin='3FCECCBA6990DD8F4839403E77F14F85',userId='10000000312441',updateType='1',
    #                   orderEvent='就是我',businessState='NOTHING_TO_SAY')
    # o.reload_config()
    # o.bm_order_detail(aid=aid,order_no='ftb20201223095909585102400',vin=vin)
    o.music_order_create(tenant_id='VW',aid=aid,vin=vin,goods='101',quantity=1)
