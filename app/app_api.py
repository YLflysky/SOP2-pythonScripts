from box.base import Base
from box.lk_logger import lk
import os


class App(Base):
    '''
    ftb2.2提供给oneApp的接口
    '''
    def __init__(self,name,password,aid,token=True):
        super().__init__()
        # APP网关需要验签和token
        self.gate = True
        self.name = name
        self.password = password
        self.uid = aid
        self.mobile_url = self.read_conf('sop2_env.conf', self.env, 'one_app_host')
        # self.device_id = 'VW_HU_CNS3_GRO-63301.10.23242312_v1.0.1_v0.0.1'
        if token:
            lk.prt('开始获取token...')
            self.cdp_url = self.read_conf('sop2_env.conf', self.env, 'cdp_host')
            token_url = self.cdp_url + '/user/public/v1/login'
            self.header['Authorization'] = self.get_token(token_url, self.name, self.password,vin=None,client='APP')

    def calendar_mobile_sync(self,current_time,vin,events:list):
        '''
        APP同步用户日历事件
        :param current_time: long类型时间戳
        :param events: 事件，列表类型
        :return:
        '''
        self.header['vin'] = vin
        url = self.mobile_url + '/oneapp/calendar/public/event/sync'
        data = {'currentTime':current_time,'events':events}
        c,b = self.do_post(url,data,gateway='APP')
        print(b)
        assert c == 200
        return b

    def calendar_mobile_find_all(self,vin):
        '''
        app获取用户所有事件接口
        :return:
        '''
        self.header['vin'] = vin
        url = self.mobile_url + '/oneapp/calendar/public/event/findAll'
        code,body = self.do_get(url,None,gateway='APP')
        print(body)
        assert code == 200
        return body



    def free_access_pay(self,vin,channel,order_no):
        '''
        免密支付接口
        :param vin:
        :param channel:
        :param order_no:
        :return:
        '''
        # self.header['vin'] = vin
        # self.header['aid'] = aid
        url = self.mobile_url + '/oneapp/pay/v1/signPay'
        data = {'payChannel':channel,'orderNo':order_no,'vin':vin}
        code,body = self.do_post(url,data,gateway='APP')
        print(body)
        assert code == 200
        return body['data']

    def contract_sign(self,vin,channel,cp_seller,display_account=None):
        '''
        APP免密
        :param vin:
        :param channel:WXPAY,ALPAY
        :param cp_seller:JDO,CMCC,BM,CUCC
        :return:
        '''
        url = self.mobile_url + '/oneapp/pay/v1/agreement/passfree/sign'
        data = {'signPay':channel,'vin':vin,'cpSeller':cp_seller,'displayAccount':display_account}
        c,b = self.do_post(url,data,gateway='APP')
        self.assert_bm_msg(c,b)

    def get_sign_result(self,vin,channel,cp_seller):
        '''
        获取免密签约状态
        :param vin:
        :param channel: WXPAY,ALPAY
        :param cp_seller:JDO,CMCC,BM,CUCC
        :return:
        '''

        url = self.mobile_url + '/oneapp/pay/v1/agreement/passfree/query'
        data = {'signPay': channel, 'vin': vin, 'cpSeller': cp_seller}
        c, b = self.do_post(url, data,gateway='APP')
        self.assert_bm_msg(c, b)
        return b

    def release_sign(self,vin,channel,cp_seller):
        '''
        免密解约
        :param vin:
        :param channel: WXPAY,ALPAY
        :param cp_seller:JDO,CMCC,BM,CUCC
        :return:
        '''

        url = self.mobile_url + '/oneapp/pay/v1/agreement/passfree/closeSign'
        data = {'signPay': channel, 'vin': vin, 'cpSeller': cp_seller}
        c, b = self.do_post(url, data,gateway='APP')
        self.assert_msg(c, b)

    def apply_invoice(self,order_no,i_channel,i_type,i_title,tax,email,**kwargs):
        '''
        APP申请开票接口
        :param order_no:
        :param i_channel:
        :param i_type:
        :param i_title:
        :param tax:
        :param email:
        :param kwargs:
        :return:
        '''
        url = self.mobile_url + '/oneapp/invoice/v1/apply'
        data = {'orderNo':order_no,'invoiceChannel':i_channel,'invoiceType':i_type,'invoiceTitle':i_title,'taxNumber':tax
                ,'email':email,**kwargs}

        c,b = self.do_post(url,data,gateway='APP')
        self.assert_bm_msg(c,b)

    def get_pay_url(self,order_no,channel):
        '''
        APP获取支付url
        :param order_no:
        :param channel:QR_ALIPAY,QR_WEIXIN
        :return:
        '''
        url = self.mobile_url + '/oneapp/pay/v1/payInfo'
        data = {'payChannel':channel,'orderNo':order_no}
        c,b = self.do_post(url,data,gateway='APP')
        self.assert_bm_msg(c,b)
        return b

    def get_order_list(self,orderStatus,orderCategoryList,tenantIdList):
        '''
        APP获取支付url
        :param order_no:
        :param channel:QR_ALIPAY,QR_WEIXIN
        :return:
        '''
        url = self.mobile_url + '/oneapp/order/v1/list'
        data = {'orderStatus':orderStatus,'orderCategoryList':orderCategoryList,'tenantIdList':tenantIdList}
        c,b = self.do_post(url,data,gateway='APP')
        self.assert_bm_msg(c,b)
        return b
    def get_order_detail(self,orderNo):
        '''
        APP获取支付url
        :param order_no:
        :param channel:QR_ALIPAY,QR_WEIXIN
        :return:
        '''
        url = self.mobile_url+'/oneapp/order/v1/detail'
        data = {'orderNo':orderNo}
        c,b = self.do_get(url,data,gateway='APP')
        self.assert_bm_msg(c,b)
        return b

    def do_order_delete(self,orderNo):

        url = self.mobile_url+'/oneapp/order/v1/delete'
        data = {'orderNo':orderNo}
        c,b = self.do_post(url,data,gateway='APP')
        self.assert_bm_msg(c,b)
        return b

    def do_order_cancel(self,orderNo):

        url = self.mobile_url+'/oneapp/order/v1/cancel'
        data = {'orderNo':orderNo}
        c,b = self.do_post(url,data,gateway='APP')
        self.assert_bm_msg(c,b)
        return b

    def create_order(self, goods_id, category, vin, count, **kwargs):
        '''
        APP创建商品订单接口
        :param goods_id:商品ID，orderCategory为PAID_CONTENT，priceType为2时，为专辑号，priceType为1时，为音频编号用“,”隔开其他均为商品ID
        :param category:商品类型（MUSIC_VIP，RADIO_VIP，WIFI_FLOW，MEDIA_FLOW，PAID_CONTENT）
        :param price_type:支付方式1音频,2整张专辑orderCategor为PAID_CONTENT，priceType必传
        :param quantity:商品数量
        :param point:是否使用积分抵扣
        :param kwargs:
        :return:
        '''
        url = self.mobile_url + '/oneapp/order/v1/create'
        data = {'goodsId': goods_id, 'vin': vin, 'orderCategory': category, 'count': count,**kwargs}
        c, b = self.do_post(url, data,gateway='APP')
        self.assert_bm_msg(c, b)
        return b

    def order_detail(self,order_no):
        url = self.mobile_url + '/oneapp/order/v1/detail'
        data = {'orderNo':order_no}
        c,b = self.do_get(url,data,gateway='APP')
        self.assert_bm_msg(c,b)
        return b

    def get_invoice_info(self,order_no):
        url = self.mobile_url + '/oneapp/invoice/v1/info'
        data = {'orderNo':order_no}
        c,b = self.do_post(url,None,data,gateway='APP')
        self.assert_bm_msg(c,b)

if __name__ == '__main__':
    import json
    os.environ['ENV'] = 'UAT'
    # app = App(name='15144142651',password='Qq111111',aid='4614233')
    app = App(name='19900001122',password='111111',aid='4614910')
    # app = App(name='15330011918',password='000000',aid='4614183',token=True)
    # app = App(name='13618079403',password='xyz2020',aid='15867227',token=True)
    vim_bm = 'LFV2A2BUXL4651255'
    vim_ma = 'LMGLS1G53H1003120'
    vim_sop1 = 'LFVUB9E75L5368051'
    # app.order_detail(order_no='ma20210514094945242778240')
    # app.contract_sign(vin=vim_bm,channel='WXPAY',cp_seller='CMCC',display_account=1)
    app.apply_invoice(order_no='ma20210615083909326704512',i_type=1,i_channel='MNO',i_title='开票',tax='445678909876543',email='995939534@qq.com',mobile='18623459409',mailingAddress='new')
    # app.get_sign_result(vin='LFV2A2BUXL4651255',channel='WXPAY',cp_seller='CMCC')
    # app.release_sign(vin='LFVSOP2TESTLY0002',channel='ALPAY',cp_seller='JDO')
    # app.get_invoice_info(order_no='ftb20210610145600261151552')
    # event = {'localEventId': app.f.pyint(100, 1000), 'cudStatus': 'C','rrule':'Only Once',
    #                  'eventStartTime': app.get_time_stamp(days=-1), 'eventEndTime': app.get_time_stamp(days=1)}
    # events = [event]
    # with open('../data/calendar_events.json', 'r', encoding='utf-8') as json_f:
    #     events = json.load(json_f)
    # print(events)
    # app.calendar_mobile_sync(current_time=None,events=events,vin='LFVTB9E67L5200138')
    # app.calendar_mobile_find_all('LFVTB9E67L5200138')
    # app.free_access_pay(vin='LFV2A2BUXL4651255',channel='ALPAY',order_no='ftb2021040911024205240960')
    # app.create_order(goods_id='17',category='MUSIC_VIP',vin=vim_bm,count=1,durationDays=3)
    # app.create_order(goods_id='1010500100000535429',category='RADIO_VIP',vin=vim_bm,count=1)
    # wifi_order=app.create_order(goods_id='cc50badd5bd6418b9c431f87394640fe',category='WIFI_FLOW',vin=vim_ma,count=1)['data']['orderNumber']
    # app.get_pay_url(order_no='ma20210514094945242778240',channel='QR_ALIPAY')
    # app.get_order_list(orderStatus=None,orderCategoryList=None,tenantIdList=None)
    # app.get_order_detail(orderNo='M202105071631161944805477')
    # app.do_order_cancel(orderNo='ma2021051915502634561440')


