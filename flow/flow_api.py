from box.base import Base


class Flow(Base):

    def __init__(self):
        super().__init__()

        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
        self.flow_url = self.read_conf('sop2_env.conf', self.env, 'flow_host')
        self.cp_url = self.read_conf('sop2_env.conf', self.env, 'cp_host')

    def assert_msg(self, code, body):
        print(body)
        assert code == 200

    def bm_get_flow_detail(self, goods_id):
        '''
        BM适配层获取流量详情接口
        '''
        url = self.hu_url + '/goods/api/v2/products/{}/detail'.format(goods_id)
        code, body = self.do_get(url, params=None)
        self.assert_msg(code,body)
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
        self.assert_msg(code,body)
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
        self.assert_msg(c,b)
        return b



    def flow_sim_notify(self,id,date,rule,asset_type,asset_id,package_id,vin):
        '''
        流量使用达到阈值回调接口
        :param id:请求id
        :param date:回调时间
        :param rule:百分比
        :param asset_type:卡类型
        :param asset_id:卡类型id
        :param package_id:套餐id
        :param vin:车辆vin码
        :return:
        '''
        url = self.flow_url + '/cmcc/notify/custSimNotification'
        data ={'requestId':id,'requestDateTime':date,'notificationFlagRule':rule,'assetType':asset_type,
               'assetId':asset_id,'packageId':package_id,'vin':vin}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def cp_sim_notify(self,id,date,rule,asset_type,asset_id,package_id):
        '''
        cp-adapter流量达到阈值回调接口，根据accId确定是否sop1的回调或者ftb2.2回调
        :param id: 当前请求的ID
        :param date:时间戳
        :param rule:已使用的百分比
        :param asset_type:取值为:iccid, msisdn, imsi
        :param asset_id:卡类型值
        :param package_id:套餐id
        :return:
        '''
        url = self.cp_url + '/flow/notify/cust_sim_notification'
        data = {'requestId': id, 'requestDateTime': date, 'notificationFlagRule': rule, 'assetType': asset_type,
                'assetId': asset_id, 'packageId': package_id}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
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
        self.assert_msg(c,b)
        return b

    def cp_sign_result_notify(self,user_id,channel,notify_type,status,enterprise='2100010000'):
        '''
        cp-adapter回调流量签约结果，同时回调到sop1和ftb2.2
        :param user_id: 用户id
        :param channel: 签约渠道1支付宝2微信
        :param notify_type: 通知类型1签约2解约
        :param status:当前状态1已签约2已解约
        :param enterprise:企业id
        :return:
        '''
        url = self.cp_url + '/flow/notify/contract_result_notify'
        data = {'userId':user_id,'channel':channel,'enterpriseId':enterprise,'notifyType':notify_type,'contractStatus':status}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def common_callback(self, id, category, status, origin_id, additional_attrs,enterprise_id='2100010000',):
        url = self.flow_url + '/cmcc/notify/commonNotification'
        data = {'enterpriseId': enterprise_id,
                'multiRecords': [{'id': id, 'idCategory': category, 'status': status, 'originalRequestId': origin_id,
                                  'additionalAttrs':additional_attrs}]}

        c, b = self.do_post(url, data)
        self.assert_msg(c,b)
        return b

    def cp_common_notify(self,id, category, status, origin_id,enterprise_id='2100010000',):
        '''
        cp-adapter流量通用回调接口,根据originalRequestId回调到sop1或者ftb2.2
        :param id:单据号
        :param category:单据类型1表示支付结果
        :param status:单据状态1000_00表示支付成功,1000_01支付失败
        :param origin_id:原请求流水号
        :param enterprise_id:企业编号
        :return:
        '''
        url = self.cp_url + '/flow/notify/common_notification'
        success_attr = {'thirdPartyPaymentSerial': 'qq995939534', 'payChannel': 'ALI_PAY',
                        'paidTime': self.time_delta(formatted='%Y%m%d%H%M%S')}
        data = {'enterpriseId': enterprise_id,
                'multiRecords': [{'id': id, 'idCategory': category, 'status': status, 'originalRequestId': origin_id,
                                  'additionalAttrs': success_attr}]}

        c, b = self.do_post(url, data)
        self.assert_msg(c,b)
        return b

if __name__ == '__main__':
    import os
    import random
    from order.payment import Payment
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    flow = Flow()
    pay = Payment()
    success_attr={'thirdPartyPaymentSerial':'qq995939534','payChannel':'ALI_PAY','paidTime':flow.time_delta(formatted='%Y%m%d%H%M%S')}
    # flow.common_callback(id=1, category=1, status='1000_00', origin_id='8ba0df0bf47f4c9fa258ea63decb3c7a',
    #                      additional_attrs=success_attr)
    # flow.flow_detail(100)
    # flow.goods_list(['WIFI_FLOW'])
    # flow.bm_get_flow_detail('268')
    # aid = 'sergio8740'
    # flow_order = flow.bm_create_flow_order(goods_id='253',aid=aid,vin='LFVSOP2TEST000353',quantity=1)
    # order_no = flow_order['data']['orderNo']
    # pay.free_qr_code(aid,order_no,channel='QR_ALIPAY_WITHHOLDING_PAYMENT',sp_id='CMCC')
    # flow.bm_goods_list('995939534','WIFI_FLOW')
    # flow.sign_result_callback(aid=flow.f.pyint(),channel=1,notify_type=2,status=1)

    # flow.flow_sim_notify(id='1',date=flow.time_delta(formatted='%Y%m%d%H%M%S'),rule=0.5,
    #                  asset_type='iccid',asset_id='995939534',package_id='P1001123577',vin='LFV2A11KXA3030241')
    # flow.cp_sign_result_notify(user_id=flow.f.pyint(),channel=1,notify_type=2,status=1)
    flow.cp_common_notify(id=1, category=1, status='1000_00', origin_id='FTB20201126095621292978944',)
    # flow.cp_sim_notify(id='1',date=flow.time_delta(formatted='%Y%m%d%H%M%S'),rule=0.5,
    #                  asset_type='iccid',asset_id='995939534cmcctest001x',package_id='P1001123577')
