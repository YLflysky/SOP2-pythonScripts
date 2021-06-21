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
        self.assert_bm_msg(c,b)
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
        c,b = self.do_put(url,None)
        self.assert_bm_msg(c,b)

    def bm_delete_order(self,aid,order_no):
        '''
        BM车机端删除订单
        :param aid: 大众用户Id
        :param order_no:订单号
        :return:
        '''
        url = self.hu_url + '/order/api/v1/orders/{}'.format(order_no)
        self.header['aid'] = aid
        c,b = self.do_delete(url,None)
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
    from order.bm_payment import BMPayment
    os.environ['ENV'] = 'UAT'
    os.environ['GATE'] = 'false'
    o = BMOrder()
    pay = BMPayment()
    xmly_aid = '9355005'
    kuwo_aid = '4614910'
    vin = 'LFV2A2BUXL4651255'
    # o.bm_update_pay(bm_order='20200921133430118139264',aid='U002',pay_no='yinli18623459409',channel=1,pay_amount=0.01,state=1,
    #                 pay_time=o.time_delta(),order_amount=0.01,orderStatus='PAY_SUCCESS')
    # o.order_list(vin='LFVSOP2TESTLY0018',aid='9353750',pageSize=300,pageIndex=1,orderStatus='1000',orderCategory='00')
    # o.order_count(vin='LFVSOP2TESTLY0018',uid='9353813',orderStatus='1000',orderCategory='00')
    # data = {"brand": "VW", "businessExtInfo": {"message": "扩展字段测试"}, "discountAmount": "2000", "orderAmount": "20000",
    #         "orderCategory": "112",
    #         "serviceId": "serviceId002", "serviceOrderState": "serviceOrderState002",
    #         "serviceOrderStateDesc": "serviceOrderStateDesc002", "spId": "spId002", "title": "title_test002",
    #         "userId": xmly_aid, "vin": "5E5F5EDBD91F4BF8462AE2DE2E89B509",'orderStatus':'REFUND_SUCCESS'}
    # o.sync_bm_order(o.get_time_stamp(), data)
    # o.bm_cancel_order(aid='4614910',order_no='ftb20210609142443554151552')
    # o.update_bm_order(order_no='ftb2021012216115830090112',vin='8099B3B73CF8EE0E85865D4EBD78C913',userId='123',updateType='1',
    #                   businessState='success',businessStateDesc='已完成')
    # o.reload_config()
    # o.bm_order_detail(aid='122',order_no='ftb20210602100240367151552',vin=None)
    # o.bm_delete_order(aid='9349485',order_no='ftb20210315155832237913408')
    order_no = o.goods_order_create(tenant_id='VW',aid=xmly_aid,vin=vin,goods='273',quantity=1)['data']['orderNo']
    # order_no = o.goods_order_create(tenant_id='VW',aid=kuwo_aid,vin=vin,goods='226',quantity=1)['data']['orderNo']
    # order_no = o.goods_order_create(tenant_id='VW',aid=kuwo_aid,vin=vin,goods='253',quantity=1)['data']['orderNo']
    # pay.get_qr_code(vin,aid=kuwo_aid,order_no='ftb20210609135827683151552',pay_type='12100',category='110')
