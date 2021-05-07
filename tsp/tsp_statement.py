from box.base import Base
import os

class Statement(Base):
    def __init__(self):
        super().__init__()
        self.url = self.read_conf('ftb3_env.conf',self.env,'statement_host')

    def statement_list(self,third_name,**kwargs):
        url = self.url + '/statement/list'
        data = {'thirdName':third_name,**kwargs}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)




if __name__ == '__main__':

    os.environ['ENV'] = 'DEV'
    os.environ['GATE'] = 'false'
    s = Statement()
    s.statement_list(third_name='FLEETIN')
    # s.write_key_redis(key='123',value='456')
