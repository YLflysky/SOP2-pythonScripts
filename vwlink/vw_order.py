from box.base import Base
from box.lk_logger import lk
import os

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
            self.add_header(self.read_conf('ma_env.conf',self.env,'token_host'),user,password,vin)

    def assert_msg(self,code,body):
        assert code == 200
        print(body)
        assert body['status'] == 'SUCCEED'

class VWOrder(VWBase):
    def __init__(self, aid,user,password,vin,token=True):
        super().__init__(aid,user,password,vin,token)

        self.payment_url = self.read_conf('ma_env.conf', self.env, 'pay_host')
        self.order_url = self.read_conf('ma_env.conf', self.env, 'order_host')

    def assert_msg(self, code, body):
        print(body)
        assert 200 == code
        assert body['status'] == 'SUCCEED'

    def get_VWlist(self,beginTime,endTime,orderStatus,pagelndex,pageSize,**kwargs):
        url = 'http://192.168.133.156:30994/vwlink/hu/mobile/order/v1/orders/list'
        data = {'beginTime': beginTime,'endTime':endTime,'orderStatus':orderStatus,'pagelndex':pagelndex,'pageSize': pageSize, **kwargs}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)



if __name__ == '__main__':
    os.environ['ENV'] = 'UAT'
    VW_order = VWOrder(aid='4614233',user='15144142651',password='Qq111111',vin='LFVTESTMOSC000129',token=False)
    # VWOrder.getvw_list(beginTime='2021-01-10 06:06:43',endTime='2021-05-10 06:06:43',orderStatus='',pagelndex='1',pageSize='10')
    VWOrder.get_VWlist(beginTime='2021-01-10 06:06:43',endTime='2021-05-10 06:06:43',orderStatus=None, pagelndex='1',pageSize='10')
    # ma_order.refund(order_no='ma20210303162711260364544',aid='4614183')
    # music_order = VWOrder('4614183',user='15330011918',password='000000',vin='LFVTEST1231231231')
    # music_order.order_list(music_order.aid,status=['FINISHED'],category='01',begin=None,end=None)
    # ma_order.ma_contract_sign(channel='ALIPAY',service='03',operator='030003')