from box.base import Base
import os,sys


class TencentCar(Base):
    def __init__(self):
        super().__init__()


        self.url = self.read_conf('ma_env.conf',self.env,'car_host')

    def assert_msg(self,code,body):
        print(body)
        assert 200 == code
        assert '成功' == body['description']

    def check_vin(self,vin=None):

        url = self.url + '/api/v1/checkVin'
        data = {'vin':vin}
        code,body = self.do_post(url,data=data)
        self.assert_msg(code,body)

    def get_QRcode(self,uid,vin):
        data = {'uid':uid,'vin':vin}
        url = self.url + '/api/v1/getBindQRCodeImage'
        code,body = self.do_post(url,data)
        self.assert_msg(code,body)

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
        self.assert_msg(code, body)

    def get_info(self,uid,vin):
        '''
        绑定账号
        :param uid:用户id
        :param vin: 车辆vin码
        :return:
        '''
        data = {'uid': uid, 'vin': vin}
        url = self.url + '/mosc-tencent-mycar-sop2/api/v1/getBindInfo'
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)
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

if __name__ == '__main__':

    os.environ['GATE'] = 'true'
    os.environ['ENV'] = 'UAT'
    car = TencentCar()
    car.unbind(aid='9349825',vin='LFV3A23C9L3046742')
    # car.get_info(uid=190001,vin='LFVTESTMOSC000025')


