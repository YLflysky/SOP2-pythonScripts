from ma_api.ma_order import MABase
from box.lk_logger import lk


class MAOrderAdapter(MABase):
    def __init__(self,aid, user, password, vin,token=True):
        super().__init__(aid, user, password, vin,token)
        self.hu_url = self.read_conf('ma_env.conf', self.env, 'order_adapter_host')

    def assert_bm_msg(self,code,body):
        print(body)
        assert 200 == code
        assert body['code'] == '000000'
        assert body['description'] == '成功'

    def sync_order(self,vin,aid,service_id,sp_id,order_type,ex_order,category,title,
                   business_state,desc,amount,discount,pay_amount,business_info,**kwargs):
        '''
        MA提供的外部订单同步结果
        :param vin:
        :param aid:
        :param service_id:
        :param sp_id:
        :param order_type:
        :param ex_order:
        :param category:
        :param title:
        :param business_state:
        :param desc:
        :param amount:
        :param discount:
        :param pay_amount:
        :param business_info:
        :return:
        '''
        url = self.hu_url + '/external/v2/sync/order'
        data = {'vin':vin,'aid':aid,'serviceId':service_id,'spId':sp_id,'orderType':order_type,'exOrderNo':ex_order,
                'orderCategory':category,'title':title,'businessState':business_state,'businessStateDesc':desc,
                'amount':amount,'payAmount':pay_amount,'discountAmount':discount,'businessInfo':business_info,**kwargs}

        c,b = self.do_post(url,data)
        self.assert_msg(c,b)

    def sync_order_pay(self, aid, order_no, pay_order_no, channel, pay_type, pay_amount, pay_time, pay_status,
                       **kwargs):
        '''
        同步订单支付结果
        :param aid:
        :param order_no:
        :param pay_order_no:
        :param channel:
        :param pay_type:FREE_PASS_PAY,QR_CODE,APP,UN_KNOWN
        :param pay_amount:
        :param pay_time:
        :param pay_status:
        :param kwargs:
        :return:
        '''
        url = self.hu_url+ '/external/v2/sync/pay'

        data = {'aid': aid, 'orderNo': order_no, 'payOrderNo': pay_order_no, 'payChannel': channel,
                'payType': pay_type,
                'payAmount': pay_amount, 'payTime': pay_time, 'payStatus': pay_status, **kwargs}

        c, b = self.do_post(url, data)
        self.assert_msg(c, b)

    def update_status_finish(self,order_no):
        '''
        更改订单状态为FINISHED
        :param order_no:
        :return:
        '''

        url = self.hu_url + '/external/v2/sync/rightsOpen'

        data = {'orderNo':order_no}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)

    def update_business(self,order_no,status,desc):
        '''
        修改订单业务状态API
        :param order_no:订单号
        :param status: 业务状态
        :param desc: 业务状态描述
        :return:
        '''
        url = self.hu_url + '/external/v2/update/businessState'

        data = {'orderNo': order_no,'businessState':status,'businessStateDesc':desc}
        c, b = self.do_post(url, data)
        self.assert_msg(c,b)


    def order_detail(self,aid,order_no,vin):
        '''
        MA车机端获取订单详情
        :param aid:
        :param order_no:
        :return:
        '''

        url = self.hu_url + '/order/api/v2/vins/{}/users/{}/orders/{}'.format(vin,aid,order_no)

        c,b = self.do_get(url,None)
        self.assert_bm_msg(c,b)



    def ma_create_order(self, aid, goods_id, category, vin, quantity,point=False,**kwargs):
        '''
        SOP2MA车机端创建商品订单接口》》车机端接口
        :param goods_id:商品ID，orderCategory为PAID_CONTENT，priceType为2时，为专辑号，priceType为1时，为音频编号用“,”隔开其他均为商品ID
        :param category:商品类型（MUSIC_VIP，RADIO_VIP，WIFI_FLOW，MEDIA_FLOW，PAID_CONTENT）
        :param price_type:支付方式1音频,2整张专辑orderCategor为PAID_CONTENT，priceType必传
        :param quantity:商品数量
        :param point:是否使用积分抵扣
        :param kwargs:
        :return:
        '''
        url = self.hu_url + '/order/mos/order/api/v1/create'
        data = {'userId':aid,'goodsId': goods_id, 'vin':vin,'orderCategory': category, 'quantity': quantity, 'usedPoint': point, **kwargs}
        c, b = self.do_post(url, data)
        self.assert_bm_msg(c,b)
        return b

    def cancel_order(self,order_no):
        '''
        MA车机端取消订单接口
        :param order_no:
        :return:
        '''
        url = self.hu_url + '/order/api/v1/orders/{}/cancel'.format(order_no)
        c,b = self.do_put(url,None)
        self.assert_bm_msg(c,b)



if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'UAT'
    # ma_order = MAOrderAdapter('9349641',user='13761048895',password='000000',vin='LMGLS1G53H1003120')
    music = MAOrderAdapter('4614183',user='15330011918',password='000000',vin='LFVTEST1231231231')
    # order_no = music.ma_create_order(aid=music.aid, vin=music.vin, goods_id='17',durationTimes=1,
    #                                     category='MUSIC_VIP', quantity=1, point=False,)['data']['orderNo']
    music.ma_create_order('9349641',goods_id='cc50badd5bd6418b9c431f87394640fe',category='WIFI_FLOW',
                             vin='LMGLS1G53H1003120',quantity=1)
    # ma_order.cancel_order(order_no='ma202103031234089871040384')

    # info = {"poiId":"bd742a558ce01c47","washStoreName":"捌零靓车店"}
    # ma_order.sync_order(vin='B6B3118B019AA7AB0D8BA29E753EDAE1',aid='9349640',service_id='03',sp_id='030003',
    #                     order_type='BUSINESS',ex_order=ma_order.f.md5(),category='09',title='加油订单',
    #                     business_state='0',desc='待支付',orderStatus='FINISHED',
    #                     amount=5.00,discount=0.25,pay_amount=4.75,timeout=1000,
    #                     business_info=info)
