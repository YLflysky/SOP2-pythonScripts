
from box.base import Base
import os,sys
from box.lk_logger import lk

class Calendar(Base):
    '''
    BM日历API
    '''
    def __init__(self,tenant,name='18280024450',password='Qq111111',vin='LFVSOP2TEST000311',aid='9350195'):
        super().__init__()

        self.name = name
        self.password = password
        self.vin = vin
        self.uid = aid
        if tenant == 'BM':
            self.url = self.read_conf('sop2_env.conf',self.env,'calendar_host')

            self.device_id = 'VW_HU_CNS3_GRO-63301.10.23242312_v1.0.1_v0.0.1'
            lk.prt('开始获取token...')
            # self.header['Authorization']=self.get_token(self.name,self.password,self.vin)
            self.header['deviceId'] = self.device_id
            self.header['uid'] = self.uid

        elif tenant == 'MA':
            self.url = self.read_conf('ma_env.conf',tenant,'calendar_host')
            self.add_header(tenant=tenant)
        elif tenant == 'CLOUD':
            self.url = self.read_conf('ma_env.conf',tenant,'calendar_host')
            self.add_header(tenant=tenant)
        else:
            lk.prt('no such environment:{}'.format(tenant))
            sys.exit(-1)

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
        self.assert_msg(code,body)

    def update_event(self,event_id,s,e,**kwargs):
        url = self.url + '/api/v1/calendar/event/modify'
        data = {'id':event_id,'eventStartTime':s,'eventEndTime':e,**kwargs}
        code,body = self.do_post(url,data)
        return body

    def get_event_list(self,data):
        '''
        获取事件列表接口
        '''
        url = self.url + '/api/v1/calendar/event/getEventListBySpecifiedTime'
        code,body = self.do_get(url,data)
        print(body)
        return body

    def get_last_time(self,uid,deviceId):
        url = self.url + '/api/v1/calendar/event/getEventLastUpdatedTime'
        self.header['uid'] = uid
        self.header['deviceId'] = deviceId
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)
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

    def mobile_sync(self,data):
        url = self.url + '/public/calendar/event/sync'
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def mobile_find_all(self,uid):
        url = self.url + '/public/calendar/event/findAll'
        self.header['uid']=uid
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)
        return body['data']


if __name__ == '__main__':
    os.environ['GATE'] = 'true'
    os.environ['ENV'] = 'UAT'
    c = Calendar(tenant='CLOUD',name='19900001174',password='111111',aid='4614962',vin='TESTOAOT111122064')

    # c.mobile_sync('C')
    # c.add_event(start_time=c.get_time_stamp(days=-1),end_time=c.get_time_stamp())
    c.find_all_event(update_time=c.get_time_stamp(days=9))
