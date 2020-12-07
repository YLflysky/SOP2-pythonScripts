from box.base import Base
import os


class MACalendar(Base):
    '''
    MA日历相关API，目前支持UAT环境和云环境
    '''
    def __init__(self,name='19900001174',password='111111',vin='TESTOAOT111122064',aid='4614962'):
        super().__init__()
        self.url = self.read_conf('ma_env.conf',self.env,'calendar_host')

        self.add_header(self.env,name,password,vin)

    def find_all(self):
        '''
        MA车机端获取用户全部日历事件
        :param aid:
        :return:
        '''
        url = self.url + '/api/v1/calendar/event/findAll'
        c,b = self.do_get(url,None)
        self.assert_msg(c,b)

    def find_detail(self, id):
        """
        获取用户单个日历事件详情
        """
        url = self.url + '/api/v1/calendar/event/findDetail'
        data = {'id': id}
        code, body = self.do_get(url, data)
        print(body)
        return body

    def assert_msg(self, code, body):
        print(body)
        assert 200 == code
        assert body['code'] == '000000'
        assert body['description'] == '成功'


if __name__ == '__main__':
    os.environ['ENV'] = 'CLOUD'
    os.environ['GATE'] = 'true'
    ma_calendar = MACalendar()
    ma_calendar.find_detail(id='10086')