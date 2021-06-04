from box.base import Base
import os

class Integral(Base):
    def __init__(self):
        super().__init__()
        self.gate = True
        if os.getenv('ENV') not in ('PROD', 'PERF'):
            self.env = 'UAT'
        self.url = self.read_conf('ma_env.conf', self.env, 'hu_host')

    def intergral_query(self,aid,b_id,b_type_id,s_type_id,p_index=1,p_size=10):
        url = self.url + '/mosc-integral/internal/integral/query'
        data = {'aid':aid,'businessId':b_id,'businessTypeId':b_type_id,'scoreTypeId':s_type_id,
                'pageIndex':p_index,'pageSize':p_size}
        param = {'aid':aid}
        c,b = self.do_post(url,data,params=param)
        self.assert_bm_msg(c,b)


if __name__ == '__main__':
    os.environ['ENV'] = 'PROD'
    i = Integral()
    i.intergral_query(aid='2016917',b_id=1,b_type_id=1,s_type_id=2)
