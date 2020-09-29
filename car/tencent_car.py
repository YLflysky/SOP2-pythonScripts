from box.base import Base
import os,sys


class TencentCar(Base):
    def __init__(self):
        super().__init__()

        if os.getenv('GATE') == 'true':
            self.url = self.read_conf('sop2_env.conf',self.env,'hu_host')+'/test-access/tm'
        else:
            print('暂时不支持的环境')
            sys.exit(-1)

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

    def unbind(self,uid,vin):
        data = {'uid': uid, 'vin': vin}
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

if __name__ == '__main__':

    os.environ['GATE'] = 'true'
    os.environ['ENV'] = 'UAT'
    car = TencentCar()
    car.get_info(uid=190001,vin='LFVTESTMOSC000025')


