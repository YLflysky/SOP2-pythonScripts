from box.base import Base


class Flow(Base):

    def __init__(self):
        super().__init__()

        self.url = self.read_conf('sop2_env.conf',self.env,'flow_host')


    def get_flow_detail(self,goods_id):
        '''
        获取流量详情接口
        '''
        url = self.url + '/api/v2/products/{}/detail'.format(goods_id)

        code,body = self.do_get(url,None)
        self.assert_msg(code,body)

if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'LOCAL'
    flow = Flow()
    flow.get_flow_detail(goods_id='123')