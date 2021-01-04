
from box.base import Base

class TSPOrder(Base):
    def __init__(self, tenant='BM'):
        super().__init__(tenant)

        self.url = self.read_conf('sop2_env.conf',self.env,'tsp_host')

    def order_list(self,size=10,no=1,**kwargs):
        '''
        tsp根据条件获取订单列表
        :param kwargs:
        :return:
        '''
        url = self.url + '/tsp/order/list'
        data = {'pageSize':size,'pageNo':no,**kwargs}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def order_export(self,aid,size=10,no=1,**kwargs):
        '''
        tsp根据条件获取订单列表
        :param kwargs:
        :return:
        '''
        url = self.url + '/tsp/order/export'
        data = {'pageSize':size,'pageNo':no,**kwargs}
        self.header['aid'] = aid
        c,b = self.do_get(url,data)
        self.assert_msg(c,b)
        return b

if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'DEV'
    tsp = TSPOrder()
    # tsp.order_list()
    tsp.order_export(aid='9642113')


