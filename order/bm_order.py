from box.base import Base

class BMOrder(Base):
    '''
    BM适配层订单服务API
    '''
    def __init__(self):
        super().__init__()
        self.hu_url = self.read_conf('sop2_env.conf',self.env,'hu_host')
        self.be_url = self.read_conf('sop2_env.conf',self.env,'be_host')

    def assert_msg(self,code,body):
        print(body)
        assert code == 200
        assert body['description'] == '成功'

    def order_count(self,vin,uid,**kwargs):
        '''
        according to the order status,time returns the order quantity
        '''

        url = self.hu_url + '/order/api/v2/vins/{}/orders/count'.format(vin)
        data = {'userId':uid,**kwargs}
        code,body = self.do_get(url,data)
        print(body)
        return body

    def reload_config(self):
        '''
        重新加载category配置接口
        '''
        url = self.hu_url + '/order/api/v2/order/map/reload'
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)

    def sync_bm_order(self,bm_order_id,data):
        '''
        订单适配层同步BM订单
        '''
        url = self.be_url + '/order/api/v2/orders/{}/sync'.format(bm_order_id)

        code,body = self.do_post(url,data)
        self.assert_msg(code,body)
        return body

    def update_bm_order(self,order_no,vin,userId,updateType,**kwargs):
        '''
        BM适配层更新订单
        '''
        url = self.be_url + '/order/api/v2/orders/{}/status'.format(order_no)
        params = {'vin':vin,'userId':userId,'updateType':updateType,**kwargs}
        code,body = self.do_put(url,None,params)
        self.assert_msg(code,body)





if __name__ == '__main__':
    import os
    os.environ['ENV']='DEV'
    os.environ['GATE']='false'
    o = BMOrder()
    # o.order_count(vin=123,uid='469317')
    data = {'vin': o.f.pyint(), 'brand': o.f.word(), 'businessExtInfo': o.f.pydict(4, True, value_types=str),
            'discountAmount': '10086',
            'orderAmount': '100', 'orderCategory': 105, 'serviceId': 'GAS', 'spId': '111', 'title': o.f.sentence(),
            'userId': '469317', 'serviceOrderState': 'FINISH', 'serviceOrderStateDesc': 'jojo', }
    o.order_count(vin='DEFAULT_VIN',uid='33')
    # o.update_bm_order(order_no='20200915135838636516096',vin=o.f.pyint(),userId='qwe',updateType='1',
    #                   orderEvent='就是我',businessState='NOTHING_TO_SAY')
    # o.sync_bm_order(bm_order_id=768212448097734656)
