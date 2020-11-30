from box.base import Base
import os

class MACalendar(Base):


    def __init__(self,name='19900001174',password='111111',vin='TESTOAOT111122064',aid='4614962'):
        super().__init__()
        self.url = self.read_conf('ma_env.conf',self.env,'calendar_host')

        self.header['Authorization'] = self.get_token('MA',name, password, vin)

    def find_all(self):
        '''
        MA车机端获取用户全部日历事件
        :param aid:
        :return:
        '''
        url = self.url + '/api/v1/calendar/event/findAll'
        c,b = self.do_get(url,None)
        self.assert_msg(c,b)

    def assert_msg(self, code, body):
        print(body)
        assert 200 == code
        assert body['code'] == '000000'
        assert body['description'] == '成功'


if __name__ == '__main__':
    os.environ['ENV'] = 'UAT'
    os.environ['GATE'] = 'true'
    ma_calendar = MACalendar()
    ma_calendar.find_all()