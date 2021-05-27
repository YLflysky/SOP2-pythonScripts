
from box.base import Base

class TSPOrder(Base):
    def __init__(self):
        super().__init__()

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
        tsp导出订单
        :param kwargs:
        :return:
        '''
        url = self.url + '/tsp/order/export'
        data = {'brand':brand,'userId':aid,'userName':name,**kwargs}
        self.header['userId'] = aid
        self.header['userName'] = name
        c,b = self.do_get(url,data)
        print(b)
        assert c == 200
        return b

    def order_detail(self,aid,order_no):
        '''
        tsp查询订单详情接口
        '''
        url = self.url + '/tsp/order/detail'
        data = {'aid':aid,'orderNo':order_no}
        c,b = self.do_get(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    tsp = TSPOrder()
    tsp.order_list(size=100,orderCategoryList=['116'])
    # tsp.order_detail(aid='4606649',order_no='M201903051419301674344526')
    # tsp.order_export(aid='111',name='111',brand='VW',orderCategoryList=['114'],orderNo='ftb20210506')


