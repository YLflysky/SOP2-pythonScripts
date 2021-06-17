from box.base import Base
import os

class Violation(Base):
    def __init__(self):
        super().__init__()
        self.gate = True
        if os.getenv('ENV') not in ('PROD', 'PERF'):
            self.env = 'UAT'
        self.url = self.read_conf('ma_env.conf', self.env, 'base_url_hu') + '/mosc-violation'

    def get_vin_by_hash_vin(self,hash_vin):
        url = self.url + '/getDecrypt'
        data = {'value':hash_vin}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def create_violation_order(self):
        pass

    def get_violation_detail(self,serial_no,):
        url = self.url + '/violation-records/{}'.format(serial_no)
        c,b = self.do_get(url,None)
        self.assert_bm_msg(c,b)

    def get_violation_list(self):
        '''
        获取违章列表
        '''
        pass



if __name__ == '__main__':
    os.environ['ENV'] = 'PROD'
    vio = Violation()
    vio.get_vin_by_hash_vin(hash_vin='751C021535B7C3C3E5017ED12AECBDE1')
    # vio.get_violation_detail(serial_no='1902c408427ee0daa7b78555adb5bacc')
