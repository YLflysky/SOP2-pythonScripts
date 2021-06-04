from box.base import Base
import os,json


class CPManageSOP2(Base):
    def __init__(self):
        super().__init__()
        self.gate = True
        if os.getenv('ENV') not in ('PROD', 'PERF'):
            self.env = 'UAT'
        self.url = self.read_conf('ma_env.conf', self.env, 'hu_host')

    def get_aksk(self,data):
        '''
        获取对接SP的AKSK
        '''
        url = self.url + '/mosc-cp-manage/external/v1/getAksk'
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)






if __name__ == '__main__':
    os.environ['ENV'] = 'PROD'
    cp = CPManageSOP2()
    sp1 = {'serviceId':'03','spId':'030003'}
    sp2 = {'serviceId':'FLOW','spId':'XIMALAYA'}
    i = {'spInfos':[sp1,sp2]}
    cp.get_aksk(i)
