from box.base import Base


class Flow(Base):

    def __init__(self):
        super().__init__()

        self.hu_url = self.read_conf('sop2_env.conf',self.env,'hu_host')
        self.flow_url = self.read_conf('sop2_env.conf',self.env,'flow_host')


    def bm_get_flow_detail(self,goods_id):
        '''
        BM适配层获取流量详情接口
        '''
        url = self.hu_url + '/api/v2/products/{}/detail'.format(goods_id)
        code,body = self.do_get(url,params=None)
        assert code == 200
        print(body)
        return body

    def flow_detail(self,goods):
        '''
        flow服务底层获取
        '''
        url = self.flow_url + '/goods/detail'
        param = {'goodsId':goods}
        c,b = self.do_get(url,param)
        self.assert_msg(c,b)

if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'LOCAL'
    flow = Flow()
    flow.flow_detail('255')
    # flow.bm_get_flow_detail('254')