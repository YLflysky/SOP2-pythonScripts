
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

        if tenant == 'BM':
            self.device_id = 'VW_HU_CNS3_GRO-63301.10.23242312_v1.0.1_v0.0.1'
            self.url = self.read_conf('sop2_env.conf', self.env, 'calendar_host')
            # lk.prt('开始获取token...')
            if token:
                token_url = self.read_conf('sop2_env.conf',self.env,'token_host')
                self.header['Authorization']=self.get_token(token_url,name,password,self.vin)
                self.header['Did'] = self.device_id

        elif tenant == 'MA':
            self.gate = 'True'
            if os.getenv("ENV") not in ['PROD','PREF']:
                self.env = 'UAT'
            self.device_id = 'VW_HU_BS43C4_EPTest_Android9.0_v1.2.0'
            self.url = self.read_conf('ma_env.conf',self.env,'base_url_hu') + '/mos/37w-calendar-sop2'
            if token:
                lk.prt('开始获取token...')
                self.add_header(self.read_conf('ma_env.conf', self.env, 'token_host'),name,password,vin)
        else:
            lk.prt('不存在该车型项目……')
            sys.exit(-1)

    def find_all_event(self,update_time):
        '''
        获取用户全部日历事件
        '''
        url = 'https://mobile.mosc.faw-vw.com/prod/tm/mos/37w-calendar/public/calendar/event/findAll'
        if update_time:
            data = {'updateTime':update_time}
        else:
            data = None
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
        url = 'https://mobile.mosc.faw-vw.com/prod/tm/mos/37w-calendar/public/calendar/event/sync'
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





if __name__ == '__main__':
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'PROD'
    c = Calendar(tenant='MA',token=True,name='13618079403',password='xyz2020',vin='LFVSOP2TESTLY0040',aid='15867227')
    # c.find_detail(id='1')
    # c.get_last_time()
    # event = {'localEventId': c.f.pyint(100, 1000), 'cudStatus': 'C','rrule':'Only Once',
    #                  'eventStartTime': c.get_time_stamp(days=-1), 'eventEndTime': c.get_time_stamp(days=1)}
    # c.add_event(start_time=c.get_time_stamp(days=-1),end_time=c.get_time_stamp(days=10),events=[event])
    c.find_all_event(update_time=None)
    # data = {'apiType': 'TYPE_ONE', 'startDate': '1612763053000', 'endDate': '1618535559000'}
    # bm_c.get_event_list(data)
    # bm_c.del_event(event_id=1)
