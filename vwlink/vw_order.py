from box.base import Base
from box.lk_logger import lk
import os

lk.prt('导入 MA API 基类>>>>')

class VWBase(Base):
    def __init__(self,aid,user,password,vin,token=True):
        super().__init__()
        self.aid = aid
        self.vin = vin
        self.gate = True
        if os.getenv('ENV') not in ('CLOUD','PERF'):
            self.env = 'UAT'
        if token:
            lk.prt('开始获取token...')
            self.add_header(self.read_conf('vw_order.conf',self.env,'token_host'),user,password,vin)

    def assert_msg(self,code,body):
        assert code == 200
        print(body)
        assert body['status'] == 'SUCCEED'

class VWOrder(VWBase):
    def __init__(self, aid,user,password,vin,token=True):
        super().__init__(aid,user,password,vin,token)
        self.vworder_url = self.read_conf('vw_order.conf', self.env, 'vwlink_host')
        self.order_url = self.read_conf('ma_env.conf', self.env, 'order_host')

    def assert_msg(self, code, body):
        print(body)
        assert 200 == code
        assert body['status'] == 'SUCCEED'

    def get_VWlist(self,beginTime,endTime,orderStatus,pagelndex,pageSize,**kwargs):
        self.header['aid'] = '1234'
        url = self.order_url+'/vwlink/hu/mobile/order/v1/orders/list'
        data = {'beginTime': beginTime,'endTime':endTime,'orderStatus':orderStatus,'pagelndex':pagelndex,'pageSize': pageSize, **kwargs}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def get_VWdetail(self,orderNo,**kwargs):
        self.header['aid'] = '1234'
        url = 'http://192.168.133.156:30994/vwlink/hu/mobile/order/v1/orders/detail'
        data = {'orderNo': orderNo, **kwargs}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)



if __name__ == '__main__':
    os.environ['ENV'] = 'SIT'
    VW_order = VWOrder(aid='4614233',user='15144142651',password='Qq111111',vin='LFVTESTMOSC000129',token=False)
    # VW_order.get_VWlist(beginTime='2021-01-10 06:06:43',endTime='2021-05-10 06:06:43',orderStatus=None, pagelndex='1',pageSize='10')
    # VW_order.get_VWdetail(orderNo='ftb20210420092635290348160')
