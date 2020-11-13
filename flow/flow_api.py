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
                'multiRecords': [{'id': id, 'idCategory': category, 'status': status, 'originalRequestId': origin_id,**kwargs}]}

        c, b = self.do_post(url, data)
        print(b)
        assert 200 == c
        return b

    def get_qr_code(self,ex_order,aid,order_no,channel,pay_no,sp_id='CMCC'):
        '''
        获取流量订单支付二维码
        :param ex_order: 外部订单号
        :param aid: 用户id
        :param order_no: 订单编号
        :param channel: 支付渠道
        :param sp_id: CMCC
        :param pay_no: 支付流水号
        :return:
        '''
        url = self.flow_url+'/order/qrCode'
        data = {'exOrderNo':ex_order,'aid':aid,'orderNo':order_no,'payChannel':channel,'spId':sp_id,'payNo':pay_no}

        c,b = self.do_post(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':
    import os

    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'DEV'
    flow = Flow()
    # flow.get_qr_code('e00c66a3ad7a4964911cbaf475bcca9b','111','20201113094813034827392','ALI_PAY',flow.f.md5())
    success_attr={'thirdPartyPaymentSerial':'qq995939534','payChannel':'ALI_PAY','paidTime':flow.time_delta(formatted='%Y%m%d%H%M%S')}
    # flow.common_callback(id=1, category=1, status='1000_00', origin_id='8ba0df0bf47f4c9fa258ea63decb3c7a',
    #                      additionalAttrs=success_attr)
    flow.flow_detail(10010)
    # flow.bm_get_flow_detail('100')
    # flow.sign_result_callback(aid=flow.f.pyint(),channel=1,notify_type=2,status=1)
