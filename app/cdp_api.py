from box.base import Base

class CDP(Base):
    def __init__(self, tenant='BM'):
        super().__init__()
        self.gate = True
        self.cdp_url = self.read_conf('sop2_env.conf', self.env, 'cdp_host')
        if self.env =='UAT':
            namespace = 'cdp-uat'
        else:
            namespace = 'production'
        self.header['x-namespace-code'] = namespace
        self.header['x-microservice-name'] = 'api-gateway'

    def get_vin_by_iccid(self,iccid):
        '''
        cdp根据iccid获取vin接口
        :param iccid:
        :return:
        '''

        url = self.cdp_url + '/vehicle/internal/v1/getVinByIccid'
        data = {'iccid':iccid}

        c,b = self.do_get(url,data,gateway='CDP')
        self.assert_bm_msg(c,b)


    def get_iccid_by_vin(self,vin):
        '''
        cdp根据iccid获取vin接口
        :param iccid:
        :return:
        '''

        url = self.cdp_url + '/vehicle/internal/v1/getIccidByVin'
        data = {'vin':vin}

        c,b = self.do_get(url,data,gateway='CDP')
        self.assert_bm_msg(c,b)

    def ger_qr_code(self,goods_id,):
        pass

if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'PROD'
    cdp = CDP()
    # cdp.get_vin_by_iccid(iccid='89860802092030685837')
    cdp.get_iccid_by_vin(vin='LFV2A2BUXL4651255')
    # cdp.get_iccid_by_vin(vin='LFV2A2BU2L4444083')
