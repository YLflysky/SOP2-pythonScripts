from box.base import Base
from box.lk_logger import lk
import os


class App(Base):
    '''
    ftb2.2提供给oneApp的接口
    '''
    def __init__(self,name,password,aid):
        super().__init__()
        # APP网关需要验签和token
        self.gate = True
        self.name = name
        self.password = password
        self.uid = aid
        # self.header['aid'] = aid
        self.mobile_url = self.read_conf('sop2_env.conf', self.env, 'one_app_host')
        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
        self.device_id = 'VW_HU_CNS3_GRO-63301.10.23242312_v1.0.1_v0.0.1'
        lk.prt('开始获取token...')
        self.cdp_url = self.read_conf('sop2_env.conf', self.env, 'cdp_host')
        token_url = self.cdp_url + '/user/public/v1/login'
        self.header['Authorization'] = self.get_token(token_url, self.name, self.password,vin=None,client='APP')
        self.header['Did'] = self.device_id

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

    def get_tenant_by_vin(self,vin):
        '''
        根据vin码获取到是哪个项目的车型
        :return:
        '''
        url = self.hu_url + '/vs/ftb-vehicle/public/v1/tenant/get_by_vin'
        data = {'vin':vin}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)
        return b['data']['tenantId']

    def free_access_pay(self,aid,vin,channel,order_no):
        '''
        免密支付接口
        :param vin:
        :param channel:
        :param order_no:
        :return:
        '''
        self.header['vin'] = vin
        self.header['aid'] = aid
        url = self.mobile_url + '/oneapp/pay/v1/signPay'
        data = {'payChannel':channel,'orderNo':order_no}
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


if __name__ == '__main__':
    import json
    os.environ['ENV'] = 'UAT'
    app = App(name='13761048895',password='000000',aid='9349641')
    # app.contract_sign(vin='LFVSOP2TESTLY0002',channel='ALPAY',cp_seller='JDO')
    app.apply_invoice(order_no='ma20210225094735194245760',i_type='PERSONAL',i_channel='JDO',i_title='开票',tax='445678909876543',email='995939534@qq.com',mobile='18623459409')
    # app.get_sign_result(vin='LFVSOP2TESTLY0002',channel='ALPAY',cp_seller='JDO')
    # app.release_sign(vin='LFVSOP2TESTLY0002',channel='ALPAY',cp_seller='JDO')
    # app.get_tenant_by_vin(vin='LFVSOP2TESTLY0003')

    # event = {'localEventId': app.f.pyint(100, 1000), 'cudStatus': 'C','rrule':'Only Once',
    #                  'eventStartTime': app.get_time_stamp(days=-1), 'eventEndTime': app.get_time_stamp(days=1)}
    # with open('../conf/calendar_events.json', 'r', encoding='utf-8') as json_f:
    #     events = json.load(json_f)
    # print(events)
    # app.calendar_mobile_sync(current_time=None,events=events,vin='LFVSOP2TESTLY0049')
    # app.calendar_mobile_find_all('LFVSOP2TESTLY0049')
    # app.free_access_pay(aid='9353497',vin='LFVSOP2TESTLY0002',channel='WXPAY',order_no='20210201172351827405504')


