from box.base import Base
from box.lk_logger import lk
import json,os

lk.prt('导入 MA API 基类>>>>')


class MABase(Base):
    def __init__(self,aid,user,password,vin,token=True):
        super().__init__()
        self.aid = aid
        self.vin = vin
        self.gate = True
        if os.getenv('ENV') not in ('PERF','PROD'):
            self.env = 'UAT'
        if token:
            lk.prt('开始获取token...')
            token_url = self.read_conf('ma_env.conf',self.env,'base_url_login') + '/user/api/v1/token'
            self.add_header(token_url,user,password,vin)
        self.hu_url = self.read_conf('ma_env.conf', self.env, 'base_url_hu')
        self.backend_url = self.read_conf('ma_env.conf', self.env, 'base_url_back')

    def assert_msg(self,code,body):
        print(json.dumps(body,indent=4))
        assert code == 200
        assert body['status'] == 'SUCCEED'
