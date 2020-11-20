from box.base import Base


class Flow(Base):

    def __init__(self):
        super().__init__()

        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
        self.flow_url = self.read_conf('sop2_env.conf', self.env, 'flow_host')
        self.cp_url = self.read_conf('sop2_env.conf', self.env, 'cp_host')

    def bm_get_flow_detail(self, goods_id):
        '''
        BM适配层获取流量详情接口
        '''
        url = self.hu_url + '/goods/api/v2/products/{}/detail'.format(goods_id)
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
        流量底层免密签约结果回调
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
        url = self.flow_url + '/cmcc/notify/commonNtify'
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

    def goods_list(self,categories:list):
        '''
        flow服务获取商品列表
        :param categories:商品类型，列表形式
        :return:
        '''
        url = self.flow_url + '/goods/list'
        param = {'categories':categories}
        c,b = self.do_get(url,param)
        self.assert_msg(c,b)
        return b

    def bm_goods_list(self,aid,categories):
        '''
        BM车机端获取流量商品列表
        :param aid: 用户id
        :param categories: 商品类型，列表形式
        :return:
        '''
        url = self.hu_url + '/goods/api/v2/users/{}/vins/{}/products/list'.format(aid,self.random_vin())
        param = {'productType':categories}
        code,body = self.do_get(url,param)
        print(body)
        return body

    def bm_create_flow_order(self,goods_id,aid,vin,quantity):
        '''
        BM车机端创建流量订单
        :param goods_id: 商品ID
        :param aid:大众用户id
        :param vin:车架号
        :param quantity:购买数量
        :return:
        '''
        url = self.hu_url + '/goods/api/v1/orderCreate'
        data = {'goodsId':goods_id,'userId':aid,'vin':vin,'quantity':quantity}
        self.header['aid'] = aid
        c,b = self.do_post(url,data)
        print(b)
        assert c == 200
        return b

    def flow_notify(self,id,date,rule,asset_type,asset_id,package_id,vin):
        url = self.flow_url + '/cmcc/notify/custSimNotification'
        data ={'requestId':id,'requestDateTime':date,'notificationFlagRule':rule,'assetType':asset_type,
               'assetId':asset_id,'packageId':package_id,'vin':vin}
        c,b = self.do_post(url,data)
        print(b)
        assert c == 200
        return b

    def cp_sign_result_notify(self,user_id,channel,notify_type,status,enterprise='2100010000'):
        url = self.cp_url + '/notify/CI_ContractResultNotify'
        data = {'userId':user_id,'channel':channel,'enterpriseId':enterprise,'notifyType':notify_type,'contractStatus':status}
        c,b = self.do_post(url,data)
        print(b)
        assert c == 200
        return b


if __name__ == '__main__':
    import os
    import random

    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'DEV'
    flow = Flow()
    # flow.get_qr_code('e00c66a3ad7a4964911cbaf475bcca9b','111','20201113094813034827392','ALI_PAY',flow.f.md5())
    success_attr={'thirdPartyPaymentSerial':'qq995939534','payChannel':'ALI_PAY','paidTime':flow.time_delta(formatted='%Y%m%d%H%M%S')}
    flow.common_callback(id=1, category=1, status='1000_00', origin_id='8ba0df0bf47f4c9fa258ea63decb3c7a',
                         additionalAttrs=success_attr)
    # flow.flow_detail(100)
    # flow.goods_list(['WIFI_FLOW'])
    # flow.bm_get_flow_detail('100')
    # flow.bm_create_flow_order(goods_id='5b7cf4f565914cab86cf71ef9ca34e99',aid='qq995939534',vin='LFVSOP2TEST000353',quantity=1)
    # flow.bm_goods_list('995939534','WIFI_FLOW')
    # flow.sign_result_callback(aid=flow.f.pyint(),channel=1,notify_type=2,status=1)

    # flow.flow_notify(id='1',date=flow.time_delta(formatted='%Y%m%d%H%M%S'),rule=0.5,
    #                  asset_type='iccid',asset_id='995939534',package_id='P1001123577',vin='LFV2A11KXA3030241')
    # flow.cp_sign_result_notify(user_id=flow.f.pyint(),channel=1,notify_type=2,status=1)