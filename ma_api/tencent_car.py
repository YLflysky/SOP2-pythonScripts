from box.base import Base
import os,sys


class TencentCar(Base):
    def __init__(self,user='15330011918',password='000000',vin='LFVTEST1231231231',aid='4614183'):
        super().__init__()
        self.env = os.getenv('ENV')
        self.url = self.read_conf('ma_env.conf',self.env,'car_host')
        self.add_header(url=self.read_conf('ma_env.conf',self.env,'token_host'),user=user,password=password,vin=vin)

    def assert_ma_msg(self,code,body):
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

    def send_poi_hu(self,vin):
        '''
        发送POI到MQTT_CENTER
        :param vin:
        :return:
        '''
        url = self.url + '/api/v1/sendMapPoi'
        data = {'poiId':2,'vin':vin,'deviceName':'ABCED','poiName':'bind','longitude':33.33,'latitude':33.33,'address':'Chengdu'}
        c,b = self.do_post(url,data)
        self.assert_ma_msg(c,b)

if __name__ == '__main__':

    import os
    os.environ['ENV'] = 'CLOUD'
    car = TencentCar()
    uid = '4614963'
    vin = None
    # car.check_vin(vin)
    # car.get_QRcode(uid,vin)
    car.send_poi_hu(vin)
    # car.unbind(uid,vin=vin)
    # car.get_info(uid,vin)
    # car.bind_callback(aid='4614963',vin='B0EEE94911E24DFA3D39B21BBFAE6506',wecar_id=None,action='abc')


