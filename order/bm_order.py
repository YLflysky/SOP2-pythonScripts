from box.base import Base

class BMOrder(Base):
    '''
    BM适配层订单服务API
    '''
    def __init__(self):
        super().__init__()
        self.url = self.read_conf('sop2_env.conf',self.env,'order_hu_host')

    def assert_msg(self,code,body):
        print(body)
        assert code == 200
        assert body['description'] == '成功'

    def order_count(self,vin,uid,**kwargs):
        '''
        according to the order status,time returns the order quantity
        '''

        url = self.url + '/api/v2/vins/{}/orders/count'.format(vin)
        data = {'userId':uid,**kwargs}
        code,body = self.do_get(url,data)
        print(body)
        return body

    def reload_config(self):
        '''
        重新加载category配置接口
        '''
        url = self.url + '/api/v2/order/map/reload'
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)


if __name__ == '__main__':
    import os
    os.environ['ENV']='DEV'
    os.environ['GATE']='false'
    o = BMOrder()
    o.order_count(vin='LFVSOP2TEST000311',uid='4614907')
