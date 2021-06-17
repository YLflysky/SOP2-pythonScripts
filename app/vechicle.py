from box.base import Base

class Vechicle(Base):

    def __init__(self,aid,name,password,vin,token=True):
        super().__init__()
        self.vehicle_url = self.read_conf('sop2_env.conf', self.env, 'vehicle_host')
        if token:
            self.aid = aid
            self.vin = vin
            token_url = self.read_conf('sop2_env.conf',self.env,'token_host')
            self.add_header(token_url,name,password,vin)

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

    def update_plate_no(self,num):
        '''
        车机端修改用户车牌号
        '''
        url = self.vehicle_url + '/vs/vehicle/api/v1/vehicle/update/plateno'
        data = {'vin':self.vin,'aid':self.aid,'plate':num}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)




if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    v= Vechicle(aid='914',vin='LFV2A11K373053899',name='15566938326',password='test1234',token=False)
    # v.update_plate_no(num='渝CR3683')
    # v.get_tenant_by_vin(vin='LFV3A23C913046742')
    v.get_hashVin_by_vin('LFVTEST1231231231')
    # v.get_vin_by_hashvin('5812E6EFA924DFEBD501D561DD011F66')
