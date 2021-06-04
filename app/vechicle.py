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

    def get_hashVin_by_vin(self,vin):
        '''
        根据vin码获取加密之后的hashVin
        :return:
        '''
        url = self.vehicle_url + '/vs/vehicle/vehicleCustomerExpand/getEncryptionVinByVin'
        data = {'vin':vin}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)
        return b['data']['encryptionVin']

    def get_vin_by_hashvin(self,hash_vin):
        '''
        根据vin码获取加密之后的hashVin
        :return:
        '''
        url = self.vehicle_url + '/vs/vehicle/vehicleCustomerExpand/getVinByEncryptionVin'
        data = {'encryptionVin':hash_vin}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)
        return b['data']['vin']


if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    v= Vechicle()
    # v.get_tenant_by_vin(vin='BVWTDMC4220050128')
    v.get_hashVin_by_vin('LFV1A23C6L3309793')
    # v.get_vin_by_hashvin('4B87CA1D604105DF4F11A6374B30D84A')
