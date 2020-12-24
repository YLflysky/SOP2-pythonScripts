from box.base import Base
import os,sys


class TencentCar(Base):
    def __init__(self):
        super().__init__()
        self.env = 'UAT'
        self.gate = True
        self.url = self.read_conf('ma_env.conf',self.env,'car_host')
        self.add_header(url=self.read_conf('ma_env.conf',self.env,'token_host'))

    def assert_bm_msg(self,code,body):
        print(body)
        assert code == 200


    def check_vin(self,vin=None):

        url = self.url + '/api/v1/checkVin'
        data = {'vin':vin}
        code,body = self.do_post(url,data=data)
        self.assert_bm_msg(code,body)

    def get_QRcode(self,uid,vin):
        data = {'uid':uid,'vin':vin}
        url = self.url + '/api/v1/getBindQRCodeImage'
        code,body = self.do_post(url,data)
        self.assert_bm_msg(code,body)

    def unbind(self,aid,vin):
        '''
        解绑车辆
        :param aid:用户id
        :param vin: 车辆vin码
        :return:
        '''
        data = {'uid': aid, 'vin': vin}
        url = self.url + '/api/v1/unBindAccount'
        code, body = self.do_post(url, data)
        self.assert_bm_msg(code, body)

    def get_info(self,uid,vin):
        '''
        绑定账号
        :param uid:用户id
        :param vin: 车辆vin码
        :return:
        '''
        data = {'uid': uid, 'vin': vin}
        url = self.url + '/api/v1/getBindInfo'
        code, body = self.do_post(url, data)
        self.assert_bm_msg(code, body)
        return body['data']

    def bind_callback(self,aid,vin,wecar_id,action):
        '''
        绑定解绑通知回调接口
        :param aid:
        :param vin:
        :param wecar_id:
        :param action:
        :return:
        '''
        url = self.url + '/api/v1/bindNotice'
        data = {'userid':aid,'vin':vin,'wecarid':wecar_id,'action':action}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)

    def check_vin(self,vin):
        '''
        检验vin码是否可用
        :param vin:
        :return:
        '''
        url = self.url + '/api/v1/checkVin'
        data = {'vin':vin}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)


if __name__ == '__main__':

    car = TencentCar()
    uid = 'X9G-10128.11.1990010018'
    vin = 'BVWTDMC4220050137'
    # car.check_vin(vin)
    car.get_QRcode(uid,vin)
    # car.unbind(aid='190001',vin='LFVTESTMOSC000025')
    # car.get_info(uid,vin)
    # car.bind_callback(aid='4614963',vin='TEZWVEVTVElDQVMzMDk3MzY=',wecar_id='TEZWVEVTVElDQVMzMDk3MzY',action='unbind')


