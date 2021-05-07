from box.base import Base
import os

class Violation(Base):
    def __init__(self):
        super().__init__()
        self.gate = True
        if os.getenv('ENV') not in ('PROD', 'PERF'):
            self.env = 'UAT'
        self.url = self.read_conf('ma_env.conf', self.env, 'hu_host')

    def get_vin_by_hash_vin(self,hash_vin):
        url = self.url + '/mosc-violation/getDecrypt'
        data = {'value':hash_vin}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)


if __name__ == '__main__':
    os.environ['ENV'] = 'PROD'
    vio = Violation()
    vio.get_vin_by_hash_vin(hash_vin='B6B3118B019AA7AB0D8BA29E753EDAE1')
