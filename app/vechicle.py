from box.base import Base

class Vechicle(Base):

    def __init__(self):
        super().__init__()
        self.vehicle_url = self.read_conf('sop2_env.conf', self.env, 'vehicle_host')

    def get_tenant_by_vin(self,vin):
        '''
        根据vin码获取到是哪个项目的车型
        :return:
        '''
        url = self.vehicle_url + '/vs/ftb-vehicle/public/v1/tenant/get_by_vin'
        data = {'vin':vin}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)
        return b['data']['tenantId']

if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    Vechicle().get_tenant_by_vin(vin='LFVSOP2TESTLY0011')
