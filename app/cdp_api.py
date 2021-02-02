from box.base import Base

class CDP(Base):
    def __init__(self, tenant='BM'):
        super().__init__(tenant)
        self.gate = True
        self.cdp_url = self.read_conf('sop2_env.conf', 'UAT', 'cdp_host')
        self.header['x-namespace-code'] = 'cdp-uat'
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

if __name__ == '__main__':

    cdp = CDP()
    cdp.get_vin_by_iccid(iccid='89860802092031013415')
