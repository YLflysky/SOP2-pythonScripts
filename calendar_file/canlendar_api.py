
from box.base import Base
import os,sys
from box.lk_logger import lk

class Calendar(Base):
    '''
    日历API
    '''
    def __init__(self,tenant,name='18280024450',password='Qq111111',vin='LFVSOP2TEST000311',aid='9350195'):
        super().__init__(tenant)

        self.name = name
        self.password = password
        self.vin = vin
        self.uid = aid
        # self.header['uid'] = aid
        self.mobile_url = self.read_conf('sop2_env.conf', self.env, 'one_app_host')
        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')

        if tenant == 'BM':
            self.gate = True
            self.device_id = 'VW_HU_CNS3_GRO-63301.10.23242312_v1.0.1_v0.0.1'
            self.url = self.read_conf('sop2_env.conf', self.env, 'calendar_host')
            # lk.prt('开始获取token...')
            self.header['Authorization']=self.get_token(self.read_conf('sop2_env.conf',self.env,'token_host'),self.name,self.password,self.vin)
            self.header['Did'] = self.device_id

        else:
            self.env = 'UAT'
            self.gate = True
            self.device_id = 'VW_HU_BS43C4_EPTest_Android9.0_v1.2.0'
            self.url = self.read_conf('ma_env.conf',self.env,'calendar_host')

            lk.prt('开始获取token...')
            self.header['Authorization'] = self.get_token(self.read_conf('ma_env.conf',self.env,'token_host')
                ,self.name,self.password,self.vin)
            self.header['Did'] = 'VW_HU_CNS3_X9G-11111.04.2099990054_v3.0.1_v0.0.1'

    def find_all_event(self,update_time):
        '''
        获取用户全部日历事件
        '''
        url = self.url + '/api/v1/calendar/event/findAll'
        data = {'updateTime':update_time}
        code,body = self.do_get(url,data)
        print(body)
        return body

    def find_detail(self,id):
        """
        获取用户单个日历事件详情
        """
        url = self.url + '/api/v1/calendar/event/findDetail'
        data = {'id':id}
        code,body = self.do_get(url,data)
        print(body)
        return body

    def add_event(self,start_time,end_time,**kwargs):
        url = self.url + '/api/v1/calendar/event/add'
        data = {'eventStartTime':start_time,'eventEndTime':end_time,**kwargs}
        code,body = self.do_post(url,data)
        print(body)
        return body

    def del_event(self,event_id):
        url = self.url + '/api/v1/calendar/event/delete'
        data = {'id':event_id}
        code,body = self.do_delete(url,data)
        if self.tenant == 'BM':
            self.assert_msg(code,body)
        else:
            assert code == 200
            assert body['code'] == '000000'
            assert body['description'] == '成功'

    def update_event(self,event_id,s,e,**kwargs):
        url = self.url + '/api/v1/calendar/event/modify'
        data = {'id':event_id,'eventStartTime':s,'eventEndTime':e,**kwargs}
        code,body = self.do_post(url,data)
        assert code == 200
        print(body)
        return body

    def get_event_list(self,data):
        '''
        获取事件列表接口
        '''
        url = self.url + '/api/v1/calendar/event/getEventListBySpecifiedTime'
        code,body = self.do_get(url,data)
        print(body)
        return body

    def get_last_time(self):
        '''
        车机端获取用户最后更新时间接口
        :param uid: 用户id，header中
        :param deviceId: 设备id，header中
        :return:
        '''
        url = self.url + '/api/v1/calendar/event/getEventLastUpdatedTime'

        code,body = self.do_get(url,None)
        if self.tenant == 'BM':
            self.assert_msg(code,body)
        else:
            print(body)
            assert code == 200
            assert body['code'] == '000000'
        return body

    def event_list_by_rule(self,api_type,st,et,uid,deviceId):
        '''
        根据规则返回事件列表
        '''
        self.header['uid'] = uid
        self.header['deviceId'] = deviceId
        url = self.url + '/api/v1/calendar/event/getEventFissionListByMonth'
        data = {'apiType':api_type,'startDate':st,'endDate':et}
        code,body = self.do_get(url,data)
        assert 200 == code
        return body

    def mobile_sync(self,current_time,events:list):
        '''
        APP同步用户日历事件
        :param current_time: long类型时间戳
        :param events: 事件，列表类型
        :return:
        '''
        url = self.mobile_url + '/oneapp/calendar/public/event/sync'
        data = {'currentTime':current_time,'events':events}
        c,b = self.do_post(url,data,gateway='APP')
        print(b)
        assert c == 200
        return b

    def mobile_find_all(self):
        '''
        app获取用户所有事件接口
        :return:
        '''

        url = self.mobile_url + '/oneapp/calendar/public/event/findAll'
        code,body = self.do_get(url,None,gateway='APP')
        print(body)
        assert code == 200
        return body['data']

    def get_tenant_by_vin(self):
        '''
        根据vin码获取到是哪个项目的车型
        :return:
        '''
        url = self.hu_url + '/vs/ftb-vehicle/public/v1/tenant/get_by_vin'
        data = {'vin':self.vin}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)
        return b['data']['tenantId']




if __name__ == '__main__':
    os.environ['GATE'] = 'true'
    os.environ['ENV'] = 'SIT'
    b = Base(tenant='BM')
    bm_c = Calendar(tenant='BM',name='13353116624',password='000000',vin='LFVSOP2TESTLY0003',aid='9353497')
    # bm_c.get_last_time(bm_c.uid,deviceId=None)
    bm_c.get_tenant_by_vin()
    # ma_c = Calendar(tenant='MA',name='13353116624',password='000000',vin='LFVSOP2TESTLY0002',aid='9353497')
    # ma_c.get_tenant_by_vin()
    # c.find_all_event(update_time=None)
    event = {'localEventId': b.f.pyint(100, 1000), 'cudStatus': 'C','rrule':'Only Once',
                     'eventStartTime': b.get_time_stamp(days=-1), 'eventEndTime': b.get_time_stamp(days=1)}
    bm_c.mobile_sync(current_time=None,events=[event])
    # c.add_event(start_time=c.get_time_stamp(days=-1),end_time=c.get_time_stamp(days=10))
    # c.find_detail(39355)
    # c.mobile_find_all()
