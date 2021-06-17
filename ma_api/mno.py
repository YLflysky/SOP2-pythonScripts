from box.base import Base
import os,json


class MNOService(Base):
    def __init__(self):
        super().__init__()
        self.gate = True
        if os.getenv('ENV') not in ('PROD', 'PERF'):
            self.env = 'UAT'
        self.url = self.read_conf('ma_env.conf', self.env, 'base_url_hu') + '/mos/mosc-mno-service'

    def get_commodity_list(self,brand,**kwargs):
        '''
        商品列表接口
        '''
        url = self.url + '/internal/commodity/list'
        data = {'brandCode':brand,**kwargs}
        c,b = self.do_get(url,None,data=json.dumps(data))
        self.assert_bm_msg(c,b)

    def get_flow_by_iccid(self,iccid):
        '''
        根据iccid查询套餐
        '''
        url = self.url + '/internal/flow/package/query'
        data = {'iccid':iccid}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)







if __name__ == '__main__':
    os.environ['ENV'] = 'UAT'
    mno = MNOService()
    # mno.get_flow_by_iccid(iccid='1234')
    # mno.get_commodity_list(brand=None)
    # vio.get_violation_detail(serial_no='1902c408427ee0daa7b78555adb5bacc')
