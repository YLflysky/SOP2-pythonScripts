
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

    def order_export(self,aid,name,brand,**kwargs):
        '''
        tsp根据条件获取订单列表
        :param kwargs:
        :return:
        '''
        url = self.url + '/tsp/order/export'
        data = {'brand':brand,**kwargs}
        self.header['userId'] = aid
        self.header['userName'] = name
        c,b = self.do_get(url,data)
        print(b)
        assert c == 200
        return b


if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'SIT'
    tsp = TSPOrder()
    tsp.order_list(size=10000)
    # tsp.order_export(aid='111',name='111',brand='VW',orderNo='ftb20201229')


