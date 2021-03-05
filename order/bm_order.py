from box.base import Base


class BMOrder(Base):
    '''
    BM适配层订单服务API
    '''

    def __init__(self):
        super().__init__()
        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
        self.be_url = self.read_conf('sop2_env.conf', self.env, 'be_host')
        if self.gate:
            token_url = self.read_conf('sop2_env.conf',self.env,'token_host')
            self.add_header(token_url)

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

    def order_list(self,vin,aid,**kwargs):
        '''
        BM车机端查看用户订单列表
        :param vin: 车架号
        :param aid: 用户id
        :param kwargs:
        :return:
        '''

        self.header['aid'] = aid
        url = self.hu_url + '/order/api/v2/vins/{}/orders/list'.format(vin)
        data = {'userId':aid,**kwargs}

        c,b =self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def reload_config(self):
        '''
        重新加载category配置接口
        '''
        url = self.hu_url + '/order/api/v2/order/map/reload'
        code, body = self.do_get(url, None)
        self.assert_bm_msg(code, body)

    def sync_bm_order(self, ex_order_no, data):
        '''
        订单适配层同步BM订单
        '''
        url = self.be_url + '/order/api/v2/orders/{}/sync'.format(ex_order_no)

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

    def goods_order_create(self, tenant_id, aid, vin, goods, quantity):
        '''
        车机端创建商品订单
        :param tenant_id: FTB2.2
        :param aid: 大众用户id
        :param vin: 车辆vin吗
        :param goods: 商品id
        :param quantity: 商品数量
        :return:
        '''
        url = self.hu_url + '/order/api/v1/orderCreate'
        self.header['tenantId'] = tenant_id
        self.header['aid'] = aid
        # 随意传入deviceId
        self.header['deviceId'] = self.f.word()
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

    def bm_update_pay(self,bm_order,aid,pay_no,channel,pay_amount,state,pay_time,order_amount,**kwargs):
        '''
        bm后台更新订单支付结果
        :param bm_order: ex_order_no
        :param aid:
        :param pay_no:
        :param channel:支付渠道
        :param pay_amount:
        :param state:
        :param pay_time:
        :param order_amount:
        :param kwargs:
        :return:
        '''
        url = self.be_url + '/order/api/v2/orders/payResult'
        data = {'bmOrderId':bm_order,'userId':aid,'payOrderNo':pay_no,'payChannel':channel,'payAmount':pay_amount,
                'payState':state,'payTime':pay_time,'orderAmount':order_amount,**kwargs}
        c,b = self.do_put(url,data)
        self.assert_bm_msg(c,b)


if __name__ == '__main__':
    import os

    os.environ['ENV'] = 'UAT'
    os.environ['GATE'] = 'false'
    o = BMOrder()
    aid = '9353449'
    vin = 'LFVTEST1231231231'
    # o.bm_update_pay(bm_order='20200921133430118139264',aid='U002',pay_no='yinli18623459409',channel=1,pay_amount=0.01,state=1,
    #                 pay_time=o.time_delta(),order_amount=0.01,orderStatus='PAY_SUCCESS')
    # o.order_list(vin,aid,pageSize=30,pageIndex=1,orderStatus='1002',orderCategory='00')
    # o.order_count(vin=123,uid='469317')
    # data = {"brand": "VW", "businessExtInfo": {"message": "扩展字段测试"},
    #         "createdTime": "1601346979941", "discountAmount": "2000", "orderAmount": "20000", "orderCategory": "99",
    #         "serviceId": "serviceId002", "serviceOrderState": "serviceOrderState002",
    #         "serviceOrderStateDesc": "serviceOrderStateDesc002", "spId": "spId002", "title": "title_test002",
    #         "userId": aid, "vin": "5E5F5EDBD91F4BF8462AE2DE2E89B509",'orderStatus':None}
    # o.sync_bm_order(o.get_time_stamp(), data)
    # o.bm_cancel_order(aid='4614931',order_no='ftb20201203160039247753664')
    # o.order_count(vin='DEFAULT_VIN',uid='33')
    # o.update_bm_order(order_no='ftb2021012216115830090112',vin='8099B3B73CF8EE0E85865D4EBD78C913',userId=aid,updateType='1',
    #                   businessState='success',businessStateDesc='已完成')
    # o.reload_config()
    o.bm_order_detail(aid='9353464',order_no='ftb20210305114519985811008',vin=None)
    # o.goods_order_create(tenant_id='VW',aid=aid,vin=vin,goods='234',quantity=1)
