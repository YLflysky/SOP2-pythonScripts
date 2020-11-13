from box.base import Base


class Flow(Base):

    def __init__(self):
        super().__init__()

        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
        self.flow_url = self.read_conf('sop2_env.conf', self.env, 'flow_host')

    def bm_get_flow_detail(self, goods_id):
        '''
        BM适配层获取流量详情接口
        '''
        url = self.hu_url + '/api/v2/products/{}/detail'.format(goods_id)
        code, body = self.do_get(url, params=None)
        print(body)
        assert code == 200
        return body

    def flow_detail(self, goods):
        '''
        flow服务底层获取流量详情
        '''
        url = self.flow_url + '/goods/detail'
        param = {'goodsId': goods}
        c, b = self.do_get(url, param)
        self.assert_msg(c, b)
        return b

    def sign_result_callback(self, aid, channel, notify_type, status, enterprise='2100010000'):
        '''
        流量免密签约结果回调
        :param enterprise:企业id，大众为2100010000
        :param aid:大众用户id
        :param channel:支付渠道，1=支付宝，2=微信
        :param notify_type:回调类型，1=签约，2=解约
        :param status:状态，1=已签约，2=未签约
        :return:
        '''
        url = self.flow_url + '/cmcc/notify/contractResultNotify'
        data = {'enterpriseId': enterprise, 'userId': aid, 'channel': channel, 'notifyType': notify_type,
                'contractStatus': status}
        c, b = self.do_post(url, data)
        assert 200 == c
        print(b)
        return b

    def common_callback(self, id, category, status, origin_id, enterprise_id='2100010000',**kwargs):
        url = self.flow_url + '/cmcc/notify/CI_CommonNotification'
        data = {'enterpriseId': enterprise_id,
                'multiRecords': [{'id': id, 'idCategory': category, 'status': status, 'originalRequestId': origin_id,
                                  'additionalAttrs':self.f.pydict(value_types=str)}],**kwargs}
        c, b = self.do_post(url, data)
        print(b)
        assert 200 == c
        return b


if __name__ == '__main__':
    import os

    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'DEV'
    flow = Flow()
    flow.common_callback(id=1, category=1, status='1000_00', origin_id=100)
    # flow.flow_detail(10010)
    # flow.bm_get_flow_detail('255')
    # flow.sign_result_callback(aid=flow.f.pyint(),channel=1,notify_type=2,status=1)
