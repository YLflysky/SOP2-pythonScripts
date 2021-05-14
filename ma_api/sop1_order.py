from box.base import Base
from box.lk_logger import lk

class SOP1Base(Base):
    def __init__(self,aid,user,password,vin,token=True):
        super().__init__()
        self.aid = aid
        self.vin = vin
        self.gate = True
        if os.getenv('ENV') not in ('CLOUD', 'PERF', 'PROD'):
            self.env = 'UAT'
        if token:
            lk.prt('开始获取token...')
            self.add_header(self.read_conf('sop1_env.conf',self.env,'token_host'),user,password,vin)

class SOP1Order(SOP1Base):
    def __init__(self, aid, user, password, vin,token=True):
        super().__init__(aid, user, password, vin,token)
        self.payment_url = self.read_conf('sop1_env.conf', self.env, 'payment_h5_host')
        self.url = self.read_conf('sop1_env.conf', self.env, 'hu_host')
        self.mobile_url = self.read_conf('sop1_env.conf', self.env, 'one_app_host')

    def sop1_create_order(self, aid, goods_id, category, vin, quantity,point=False,**kwargs):
        '''
        SOP1车机端创建商品订单接口》》车机端接口
        :param goods_id:商品ID，orderCategory为PAID_CONTENT，priceType为2时，为专辑号，priceType为1时，为音频编号用“,”隔开其他均为商品ID
        :param category:商品类型（MUSIC_VIP，RADIO_VIP，WIFI_FLOW，MEDIA_FLOW，PAID_CONTENT）
        :param price_type:支付方式1音频,2整张专辑orderCategor为PAID_CONTENT，priceType必传
        :param quantity:商品数量
        :param point:是否使用积分抵扣
        :param kwargs:
        :return:
        '''
        url = self.payment_url + '/api/v1/createOrder'
        data = {'userId':aid,'goodsId': goods_id, 'vin':vin,'orderCategory': category, 'count': quantity, 'usedPoint': point, **kwargs}

        c, b = self.do_post(url, data)
        print(b)
        return b

    def sop1_calendar_sync(self):
        url = self.mobile_url + '/mos/calendar/public/event/sync'
        event= [{'localEventId': self.f.pyint(100, 1000), 'cudStatus': 'C','rrule':'Only Once',
                     'eventStartTime': self.get_time_stamp(days=-1), 'eventEndTime': self.get_time_stamp(days=1)}]
        data = {'currentTime': self.time_delta(), 'events': event}
        c, b = self.do_post(url, data, gateway='APP')
        self.assert_bm_msg(c,b)

    def get_qr_code(self,vin,order_no,pay_type,aid):
        '''
        获取支付二维码
        :param vin:
        :param order_no:
        :param pay_type:
        :param aid:
        :return:
        '''

        url = self.payment_url + '/api/v1/getQRCodeImage'
        data = {'vin':vin,'orderNo':order_no,'payType':pay_type,'aid':aid}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)

    def ali_pay_callback(self,out_trade_no, receipt_amount, gmt_payment, trade_no, **kwargs):
        '''

        :param out_trade_no:
        :param receipt_amount:
        :param gmt_payment:
        :param trade_no:
        :param kwargs:
        :return:
        '''
        url = self.payment_url + '/mos/internal/alipayQrCallBack'
        data = {'trade_status': 'trade_success', 'app_id': '2018091361389377', 'out_trade_no': out_trade_no,
                'receipt_amount': receipt_amount, 'gmt_payment': gmt_payment, 'trade_no': trade_no, **kwargs}
        code, body = self.do_post(url, data)
        self.assert_bm_msg(code, body)
        return body

    def get_goods_list(self,aid,vin,code,brand,product_type):
        '''
        SOP2MA车机端获取商品列表
        :param aid:
        :param vin:
        :param code:
        :param brand:
        :param product_type:
        :return:
        '''
        url = self.payment_url + '/api/v2/users/{}/vins/{}/products/list'.format(aid,vin)
        data = {'brand':brand,'productType':product_type,'shopCode':code}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def local_order_create(self):
        url = self.payment_url + '/internal/v1/order/localOrderCreate'
        data = {"aid":"4614233",
                "vin":"LFVTESTMOSC000129",
                "outOrderId":"1726545da36544908054d21171c6be28",
                "orderId":"sergio123",
                "goodsId":"cc50badd5bd6418b9c431f87394640fe",
                "goodsName":"Wi-Fi半年包",
                "goodsSpec":"【Wi-Fi半年包】",
                "goodsPrice":0.01,
                "quantity":1,
                "orderCategory":"WIFI_FLOW",
                "enterpriseId":"2100010000",
                "isUsedPoint":False,
                "deductPointNumber":0,
                "deductionAmount":0,
                "orderTitle":"Wi-Fi半年包",
                "orderDesc":"【Wi-Fi半年包】",
                "orderSubStatus":1,
                "orderStatus":"1001",
                "usefulTime":1618895233688,
                "orderPrice":0.01}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)

    def ci_common_notification(self,id, category, status, origin_id, additional_attrs, enterprise_id='2100010000'):
        url = self.payment_url + '/mos/internal/CI_CommonNotification'
        data = {'enterpriseId': enterprise_id,
                'multiRecords': [{'id': id, 'idCategory': category, 'status': status, 'originalRequestId': origin_id,
                                  'additionalAttrs': additional_attrs}]}

        c, b = self.do_post(url, data)
        self.assert_bm_msg(c,b)
        return b

    def app_order_detail(self,order_no):
        '''
        APP端获取订单详情接口
        '''
        url = self.mobile_url + '/mos/payment/public/findOrderDetial'
        data = {'orderId':order_no}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def app_invoice_info(self,order_no):
        '''
        APP端获取发票信息
        '''
        url = self.mobile_url + '/mos/payment/public/findOrderDetial'
        data = {'orderId':order_no}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def find_order_by_order_id(self,order_id):
        url = self.payment_url + '/mos/internal/findOrderItemById'
        data = {'orderId':order_id}
        c,b = self.do_get(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'UAT'
    aid = '4614183'
    vin = 'LFVTEST1231231231'
    sop1 = SOP1Order(aid,user='15330011918',password='000000',vin=vin,token=True)
    # sop1.app_order_detail('M202105110940497928365814')
    # sop1.local_order_create()
    sop1.find_order_by_order_id('M202105110940497928365814')
    # sop1.get_goods_list(aid,vin,code='MA',brand='VW',product_type='radio_vip')
    # sop1.sop1_calendar_sync()
    # no = sop1.sop1_create_order(aid=aid,vin=vin,goods_id='17',category='MUSIC_VIP',quantity=1,durationDays=1,point=False)['data']['orderNumber']
    # sop1.sop1_create_order(aid=aid,vin=vin,goods_id='ca85c936d2564debb89e52bf11692e2f',category='WIFI_FLOW',quantity=1)
    # sop1.get_qr_code(vin,order_no='M202105110940497928365814',pay_type='12100',aid=aid)
    # sop1.ali_pay_callback(out_trade_no='b959af854c5c4a68a91de20ca7d5d3a8', buyer_logon_id='995939534@qq.com',
    #                      receipt_amount=0.01, gmt_payment=sop1.time_delta(), trade_no=sop1.f.pyint())
    # success_attr = {'thirdPartyPaymentSerial': 'qq995939534', 'payChannel': 'WECHAT_PAY',
    #                 'paidTime': sop1.time_delta(formatted='%Y%m%d%H%M%S')}
    # sop1.ci_common_notification(id='ma20210420150718586229376', category=1, status='1000_00', origin_id=sop1.f.md5(),additional_attrs=success_attr)

