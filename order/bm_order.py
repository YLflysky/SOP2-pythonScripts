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

    def bm_order_detail(self,aid,order_no,vin):
        '''
        BM车机端获取订单详情接口
        '''
        url = self.hu_url+'/order/api/v2/vins/{}/users/{}/orders/{}'.format(vin,aid,order_no)
        # self.header['aid'] = aid
        self.header['Authorization'] = 'eyJraWQiOiJiYzEzZjMzNy05MjY3LTQyNTktYTQzZS02NmZkY2Q4MTc4NzQiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2lkcC11YXQubW9zYy5mYXctdncuY29tIiwiYW1yIjoicHdkIiwidHlwZSI6IkFUIiwiYXVkIjpbIlZXR01CQjAxQ05BUFAxIiwiYXV0b25hdmkuY29tIiwiWDlHLTEwMjE3LjA2LjE5OTk5OTAwMTIiXSwic3ViIjoiOTM1MTUyNCIsImlhdCI6MTYwNDkyMzUzOSwidmVyIjoiMC4wLjEiLCJ2aW4iOiJDMzE1MkQwMkZGMjlBRDgzRkI5MjJBQzE0QTRCOUM3QyIsImV4cCI6MTYwNTA5NjMzOSwianRpIjoiOTczZDI0NDAtNTRmNy00YjYyLTg1ZDgtMWEzYWU4MzNhMjM5IiwiY29yIjoiQ04iLCJhaWQiOiI5MzUxNTI0IiwidG50IjoiVldfSFVfQ05TM19YOUctMTAyMTcuMDYuMTk5OTk5MDAxMl92My4wLjFfdjAuMC4xIiwiaWR0LWlkIjoiNDEyYzQwOTktMGZkYy00MmNjLTljYjEtZWQxY2EyNWE0OTliIiwic2NwIjoiYWNjb3VudCIsInJ0LWlkIjoiY2I1ODhkMjMtMjY2NC00MWJjLTllZjUtZmIwOTM1NzIwMjc5In0.jc2jdPTpob0T1k-fUYTfDTjmZlkwdJo1QdPpyxgjKVyd6x1DiG6Pt3OZd7qngrx_2FJOoN2k8KGvdHIxhqe4EA'
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)
        return body




if __name__ == '__main__':
    import os
    os.environ['ENV']='UAT'
    os.environ['GATE']='false'
    o = BMOrder()
    # o.order_count(vin=123,uid='469317')
    data = {'vin': o.f.pyint(), 'brand': o.f.word(), 'businessExtInfo': o.f.pydict(4, True, value_types=str),
            'discountAmount': '10086',
            'orderAmount': '100', 'orderCategory': 105, 'serviceId': 'GAS', 'spId': '111', 'title': o.f.sentence(),
            'userId': '469317', 'serviceOrderState': 'FINISH', 'serviceOrderStateDesc': 'jojo', }
    # o.order_count(vin='DEFAULT_VIN',uid='33')
    # o.update_bm_order(order_no='20201104154521856385024',vin='3FCECCBA6990DD8F4839403E77F14F85',userId='10000000312441',updateType='1',
    #                   orderEvent='就是我',businessState='NOTHING_TO_SAY')
    # o.reload_config()
    o.bm_order_detail(aid='9351524',order_no='111124424523',vin='6WU7LOB55T2R5E5PL')
