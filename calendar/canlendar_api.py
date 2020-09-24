
from base import Base
import os

class Calendar(Base):

    def __init__(self):
        super().__init__()

        self.url =  self.read_conf('sop2_env.conf',self.env,'mobile_host')+'/test-access/tm/mos/37w-calendar/api/v1'


    def find_all_event(self):
        url = self.url + '/calendar/event/findAll'
        data = {'updateTime':0}
        code,body = self.do_get(url,data)
        print(body)
        # for d in body['data']:
        #     print(d['origin'])
        origin = {d['origin'] for d in body['data']['events']}
        print(origin)
        # self.assert_msg(code,body)

if __name__ == '__main__':
    os.environ['GATE']='true'
    os.environ['ENV']='UAT'
    c = Calendar()
    c.find_all_event()
