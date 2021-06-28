from box.base import Base


class Flow(Base):

    def __init__(self,tenant='BM'):
        super().__init__()
        self.tenant = tenant
        self.cp_url = self.read_conf('sop2_env.conf', self.env, 'cp_host')
        if tenant == 'BM':
            self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
            self.flow_url = self.read_conf('sop2_env.conf', self.env, 'flow_host')
        elif tenant == 'MA':
            self.gate = True
            token_url = self.read_conf('ma_env.conf', self.env, 'token_host')
            self.add_header(token_url)
            self.hu_url = self.read_conf('ma_env.conf', self.env, 'hu_host')

    def assert_msg(self, code, body):
        print(body)
        assert code == 200

    def bm_get_goods_detail(self, goods_id):
        '''
        BM适配层获取流量详情接口
        '''
        url = self.hu_url + '/goods/api/v2/products/{}/detail'.format(goods_id)
        code, body = self.do_get(url, params=None)
        self.assert_msg(code, body)
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

    def flow_detail_code(self, code,duration=None):
        '''
        flow服务底层获取流量详情
        '''
        url = self.flow_url + '/goods/detail/goodCodes'
        param = {'goodsCode': code,'durationDays':duration}
        c, b = self.do_get(url, param)
        self.assert_msg(c, b)
        return b

    def goods_list(self, categories: list):
        '''
        flow服务获取商品列表
        :param categories:商品类型，列表形式
        :return:
        '''
        url = self.flow_url + '/goods/list'
        param = {'categories': categories}
        c, b = self.do_get(url, param)
        self.assert_msg(c, b)
        return b

    def bm_goods_list(self, aid, categories:list):
        '''
        BM车机端获取流量商品列表
        :param aid: 用户id
        :param categories: 商品类型，列表形式
        :return:
        '''
        url = self.hu_url + '/goods/api/v2/users/{}/vins/{}/products/list'.format(aid, self.random_vin())
        param = {'productType': categories}
        code, body = self.do_get(url, param)
        self.assert_msg(code, body)
        return body

    def bm_create_flow_order(self, goods_id, aid, vin, quantity):
        '''
        BM车机端创建流量订单
        :param goods_id: 商品ID
        :param aid:大众用户id
        :param vin:车架号
        :param quantity:购买数量
        :return:
        '''
        url = self.hu_url + '/goods/api/v1/orderCreate'
        data = {'goodsId': goods_id, 'userId': aid, 'vin': vin, 'quantity': quantity}
        self.header['aid'] = aid
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)
        return b

    def flow_sim_notify(self, id, date, rule, asset_type, asset_id, package_id, vin):
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
        data = {'requestId': id, 'requestDateTime': date, 'notificationFlagRule': rule, 'assetType': asset_type,
                'assetId': asset_id, 'packageId': package_id, 'vin': vin}
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)
        return b

    def cp_sim_notify(self, id, date, rule, asset_type, asset_id, package_id):
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
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)
        return b

    def cp_over_due_notify(self,asset_id,asset_type,package_code,effective_time,expired_time):
        '''
        cp-adapter流量到期提醒回调接口，根据asset_id确定是否sop1的回调或者ftb2.2回调
        :param asset_id:卡的id
        :param asset_type:卡的类型，ICCID,IMSI, MSISDN,VIN，一般为ICCID
        :param package_code:套餐代码
        :param effective_time:生效时间yyyyMMdd HHmmss
        :param expired_time:失效时间yyyyMMdd HHmmss
        :return:
        '''

        url = self.cp_url + '/flow/notify/package_overdue_notification'
        detail = {'assetType':asset_type,'assetId':asset_id,'packageCode':package_code,'effectiveTime':effective_time,
                  'expiredTime':expired_time}
        data = {'packageOverdueDetail':[detail]}

        c,b = self.do_post(url,data)
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
        self.assert_msg(c, b)
        return b

    def cp_sign_result_notify(self, user_id, channel, notify_type, status, enterprise='2100010000'):
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
        data = {'userId': user_id, 'channel': channel, 'enterpriseId': enterprise, 'notifyType': notify_type,
                'contractStatus': status}
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)
        return b

    def common_callback(self, id, category, status, origin_id, additional_attrs, enterprise_id='2100010000'):
        url = self.flow_url + '/cmcc/notify/commonNotification'
        data = {'enterpriseId': enterprise_id,
                'multiRecords': [{'id': id, 'idCategory': category, 'status': status, 'originalRequestId': origin_id,
                                  'additionalAttrs': additional_attrs}]}

        c, b = self.do_post(url, data)
        self.assert_msg(c, b)
        return b

    def cp_common_notify(self, id, category, status, origin_id, channel='ALI_PAY',enterprise_id='2100010000', ):
        '''
        cp-adapter流量通用回调接口,根据originalRequestId回调到sop1或者ftb2.2
        :param id:单据号
        :param category:单据类型1表示支付结果
        :param status:单据状态1000_00表示支付成功,1000_01支付失败,2000_00表示服务开通成功
        :param origin_id:原请求流水号
        :param enterprise_id:企业编号
        :param channel:支付成功时返回,ALI_PAY,WECHAT_PAY
        :return:
        '''
        url = self.cp_url + '/flow/notify/common_notification'
        records = [{'id': id, 'idCategory': category, 'status': status, 'originalRequestId': origin_id}]
        if status == '1000_00':
            success_attr = {'thirdPartyPaymentSerial': 'qq995939534', 'payChannel': channel,
                            'paidTime': self.time_delta(formatted='%Y%m%d%H%M%S')}
            records[0].update({'additionalAttrs':success_attr})
        data = {'enterpriseId': enterprise_id,
                'multiRecords': records}
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)
        return b

    def bm_remain_flow(self,flow_type,vin):
        '''
        查询车机端剩余流量
        :param flow_type: 流量类型media,wifi
        :param vin: 车辆vin码
        :return:
        '''
        if self.tenant == 'BM':
            url = self.hu_url + '/flow/api/v1/dataflow/vehicles/{}/types/{}/remain'.format(vin,flow_type)
        else:
            url = self.hu_url + '/mos/mobiledata/api/v1/dataflow/vehicles/{}/types/{}/remain'.format(vin,flow_type)
        c,b = self.do_get(url,None)
        self.assert_msg(c,b)

    def bm_flow_list(self,aid,vin):
        self.header['aid'] = aid
        url = self.hu_url + '/flow/api/v1/dataflow/users/{}/vehicles/{}/detail'.format(aid, vin)
        c, b = self.do_get(url, None)
        self.assert_msg(c, b)

    def get_sign_result(self,aid,sp_id,channel):
        '''
        流量底层获取签约结果
        :param aid:
        :param sp_id:
        :param channel:
        :return:
        '''
        url = self.flow_url + '/query/contract/info'
        data = {'spId':sp_id,'aid':aid,'payChannel':channel}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def release_sign(self,aid,sp,channel,reason):
        '''
        流量底层免密解约
        :param aid:
        :return:
        '''
        url = self.flow_url + '/signContract/terminateContract'
        data = {'spId':sp,'aid':aid,'payChannel':channel,'reason':reason}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)

    def flow_list(self,vin,sp):
        url = self.flow_url + '/query/remain/detail'
        data = {'vin':vin,'spId':sp}
        c, b = self.do_post(url, data)
        self.assert_msg(c, b)

    def qrCode(self,aid,order,ex_order,channel,pay_no,sp='CMCC'):
        '''
        去CMCC获取支付二维码
        '''
        url = self.flow_url + '/order/qrCode'
        data = {'aid':aid,'orderNo':order,'exOrderNo':ex_order,'payChannel':channel,'payNo':pay_no,'spId':sp}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':
    import os
    import random
    from order.bm_payment import BMPayment

    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    flow = Flow('BM')
    bm_pay = BMPayment()
    # user_data = flow.read_yml('../conf','user.yml')
    # user_data = user_data['uat_zqs']
    aid = '9354317'
    goods_id = 253
    vin = 'LFVTESTMOSC052726'
    iccid = '89860802091930027461'
    # flow.release_sign(aid,sp='CMCC',channel='WECHAT_PAY',reason='测试数据')
    # flow.get_sign_result(aid,sp_id='CMCC',channel='WECHAT_PAY')
    # success_attr={'thirdPartyPaymentSerial':'qq995939534','payChannel':'WECHAT_PAY','paidTime':flow.time_delta(formatted='%Y%m%d%H%M%S')}
    # flow.common_callback(id='ftb20210309142502218860160', category=1, status='1000_00', origin_id='8ba0df0bf47f4c9fa258ea63decb3c7a',
    #                      additional_attrs=success_attr)
    # flow.flow_detail_code(code='17',duration=8)
    # flow.goods_list(['MUSIC_VIP','WIFI_FLOW'])
    # flow.bm_get_goods_detail('267')
    # flow.bm_goods_list(aid,categories=['WIFI_FLOW'])
    # flow.bm_flow_list(aid='9349559',vin='LFV2A2BUXL4485299')
    # flow.flow_list(vin,sp='CMCC')
    # flow.bm_remain_flow(flow_type='media',vin='LFV2A2BUXL4485299')

    order_no = flow.bm_create_flow_order(goods_id, aid, vin=vin, quantity=1)['data']['orderNo']
    # flow.qrCode(aid,order='ftb2021061014445628440960',ex_order='111af05652694db59e275f5ba0775e4d',channel='ALI_PAY',pay_no=flow.f.md5())
    # bm_pay.get_qr_code(vin,aid,order_no=order_no,pay_type='12100',category='112')
    # flow.bm_goods_list('995939534',['MUSIC_VIP'])
    # flow.sign_result_callback(aid,channel=1,notify_type=1,status=1)

    # flow.flow_sim_notify(id='1',date=flow.time_delta(formatted='%Y%m%d%H%M%S'),rule=0.5,
    #                  asset_type='iccid',asset_id='995939534',package_id='P1001123577',vin='LFV2A11KXA3030241')
    # flow.cp_sign_result_notify(user_id='995939534',channel=2,notify_type=2,status=2)
    # flow.cp_common_notify(id='M202106041317598799846220', category=2, status='2000_00', origin_id=flow.f.md5(),channel='WECHAT_PAY')
    # flow.cp_sim_notify(id=flow.f.md5(),date=flow.time_delta(formatted='%Y%m%d%H%M%S'),rule=0.9,
    #                    asset_type='iccid',asset_id='89860802091930027461',package_id='P1001114671')
    # flow.cp_over_due_notify(asset_id='0042',asset_type='iccid',package_code='P1001183210',
    #                         effective_time=flow.time_delta(formatted='%Y%m%d%H%M%S',days=-10),
    #                         expired_time=flow.time_delta(formatted='%Y%m%d%H%M%S',minutes=-5))
