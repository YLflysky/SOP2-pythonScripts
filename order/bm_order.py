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
        self.header['aid'] = uid
        params = {**kwargs}
        code,body = self.do_get(url,params)
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

    def bm_order_detail(self,aid,order_no,vin,token=None):
        '''
        BM车机端获取订单详情接口
        '''
        url = self.hu_url+'/order/api/v2/vins/{}/users/{}/orders/{}'.format(vin,aid,order_no)
        if aid:
            self.header['aid'] = aid
        else:
            self.header['Authorization'] = token
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)
        return body




if __name__ == '__main__':
    import os
    os.environ['ENV']='DEV'
    os.environ['GATE']='false'
    o = BMOrder()
    # o.order_count(vin=123,uid='469317')
    data = {'vin': o.f.pyint(), 'brand': 'AUDI', 'businessExtInfo': o.f.pydict(4, True, value_types=str),
            'discountAmount': '10086',
            'orderAmount': '100', 'orderCategory': 105, 'serviceId': 'GAS', 'spId': '111', 'title': o.f.sentence(),
            'userId': '469317', 'serviceOrderState': 'FINISH', 'serviceOrderStateDesc': 'jojo', }
    # o.sync_bm_order(o.f.md5(),data)
    # o.order_count(vin='DEFAULT_VIN',uid='33')
    # o.update_bm_order(order_no='20201104154521856385024',vin='3FCECCBA6990DD8F4839403E77F14F85',userId='10000000312441',updateType='1',
    #                   orderEvent='就是我',businessState='NOTHING_TO_SAY')
    # o.reload_config()
    o.bm_order_detail(aid='9349643',order_no='M202007160901278277176514',vin=o.random_vin())
