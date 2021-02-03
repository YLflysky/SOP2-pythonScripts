from box.base import Base
from box.lk_logger import lk
import os


class App(Base):
    '''
    ftb2.2提供给oneApp的接口
    '''
    def __init__(self, tenant,name,password,aid,vin):
        super().__init__(tenant)
        # APP网关需要验签和token
        self.gate = True
        self.name = name
        self.password = password
        self.uid = aid
        self.header['aid'] = aid
        self.mobile_url = self.read_conf('sop2_env.conf', self.env, 'one_app_host')
        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
        self.device_id = 'VW_HU_CNS3_GRO-63301.10.23242312_v1.0.1_v0.0.1'
        lk.prt('开始获取token...')
        token_url = self.read_conf('sop2_env.conf', self.env, 'app_token')
        self.header['Authorization'] = self.get_token(token_url, self.name, self.password,vin=vin,client='HU')
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
        return body['data']

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

if __name__ == '__main__':

    os.environ['ENV'] = 'SIT'
    app = App(tenant='BM',name='19900001111',password='111111',aid='9353497',vin='LFVSOP2TESTLY0003')

    # event = {'localEventId': app.f.pyint(100, 1000), 'cudStatus': 'C','rrule':'Only Once',
    #                  'eventStartTime': app.get_time_stamp(days=-1), 'eventEndTime': app.get_time_stamp(days=1)}
    # app.calendar_mobile_sync(current_time=None,events=[event],vin='LFVSOP2TESTLY0003')
    app.calendar_mobile_find_all('LFVSOP2TESTLY0003')


