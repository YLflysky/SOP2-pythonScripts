
from box.base import Base
import os,sys
from box.lk_logger import lk

class Calendar(Base):
    '''
    日历API
    '''
    def __init__(self,tenant,token,name='18280024450',password='Qq111111',vin='LFVSOP2TEST000311',aid='9350195'):
        super().__init__()
        self.vin = vin
        self.uid = aid
        # self.header['aid'] = aid
        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')

        if tenant == 'BM':
            self.device_id = 'VW_HU_CNS3_GRO-63301.10.23242312_v1.0.1_v0.0.1'
            self.url = self.read_conf('sop2_env.conf', self.env, 'calendar_host')
            # lk.prt('开始获取token...')
            if token:
                token_url = self.read_conf('sop2_env.conf',self.env,'token_host')
                self.header['Authorization']=self.get_token(token_url,name,password,self.vin)
                self.header['Did'] = self.device_id

        else:
            self.gate = 'True'
            self.env = 'UAT'
            self.device_id = 'VW_HU_BS43C4_EPTest_Android9.0_v1.2.0'
            self.url = self.read_conf('ma_env.conf',self.env,'calendar_host')
            if token:
                lk.prt('开始获取token...')
                self.add_header(self.read_conf('ma_env.conf', self.env, 'token_host'))
                self.header['Did'] = self.device_id

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
        self.assert_bm_msg(code,body)

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
        self.assert_bm_msg(code,body)

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




if __name__ == '__main__':
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    b = Base()
    bm_c = Calendar(tenant='BM',token=True,name='13353110049',password='000000',vin='LFVSOP2TESTLY0049',aid='9353883')
    # print(bm_c.gate)
    # bm_c.get_last_time()
    # ma_c = Calendar(tenant='MA',name='13353116624',password='000000',vin='LFVSOP2TESTLY0002',aid='9353497')
    # ma_c.get_tenant_by_vin()
    # c.find_all_event(update_time=None)
    # event = {'localEventId': b.f.pyint(100, 1000), 'cudStatus': 'C','rrule':'Only Once',
    #                  'eventStartTime': b.get_time_stamp(days=-1), 'eventEndTime': b.get_time_stamp(days=1)}
    # bm_c.mobile_sync(current_time=None,events=[event])
    # c.add_event(start_time=c.get_time_stamp(days=-1),end_time=c.get_time_stamp(days=10))
    # bm_c.find_all_event(update_time=None,)
    data = {'apiType': 'TYPE_ONE', 'startDate': '1612763053000', 'endDate': '1618535559000'}
    bm_c.get_event_list(data)
