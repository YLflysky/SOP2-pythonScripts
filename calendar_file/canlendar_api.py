
from box.base import Base
import os
from box.lk_logger import lk

class Calendar(Base):
    '''
    BM日历API
    '''
    def __init__(self,name='18280024450',password='Qq111111',vin='LFVSOP2TEST000311'):
        super().__init__()

        self.url = self.read_conf('sop2_env.conf',self.env,'calendar_host')
        if self.gate:
            self.url = self.url + '/test-access/tm/mos/37w-calendar/api/v1'
        else:
            self.url = self.url + '/api/v1'

        self.name = name
        self.password = password
        self.vin = vin
        lk.prt('开始获取token...')
        self.header['Authorization']=self.get_token(self.name,self.password,self.vin)
        self.header['Did']='VW_HU_CNS3_GRO-63301.10.23242312_v1.0.1_v0.0.1'



    def find_all_event(self,update_time):
        '''
        获取用户全部日历事件
        '''
        url = self.url + '/calendar/event/findAll'
        data = {'updateTime':update_time}
        code,body = self.do_get(url,data)
        print(body)
        return body

    def find_detail(self,id):
        """
        获取用户单个日历事件详情
        """
        url = self.url + '/calendar/event/findDetail'
        data = {'id':id}
        code,body = self.do_get(url,data)
        print(body)
        return body

    def add_event(self,start_time,end_time,**kwargs):
        url = self.url + '/calendar/event/add'
        data = {'eventStartTime':start_time,'eventEndTime':end_time,**kwargs}
        code,body = self.do_post(url,data)
        print(body)
        return body

    def del_event(self,event_id):
        url = self.url + '/calendar/event/delete'
        data = {'id':event_id}
        code,body = self.do_delete(url,data)

    def update_event(self,event_id,s,e,**kwargs):
        url = self.url + '/calendar/event/modify'
        data = {'id':event_id,'eventStartTime':s,'eventEndTime':e,**kwargs}
        code,body = self.do_post(url,data)
        return body

    def get_event_list(self,data):
        url = self.url + '/calendar/event/getEventListBySpecifiedTime'
        code,body = self.do_get(url,data)
        print(body)
        return body

if __name__ == '__main__':
    os.environ['GATE']='false'
    os.environ['ENV']='LOCAL'
    c = Calendar()

    c.del_event(38573)
