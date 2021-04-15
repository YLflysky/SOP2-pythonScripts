from ma_api.ma_order import MABase
import os,sys


class TencentCar(MABase):
    def __init__(self,aid,user,password,vin,token=True):
        super().__init__(aid,user,password,vin,token)
        self.url = self.read_conf('ma_env.conf',self.env,'car_host')

    def assert_ma_msg(self,code,body):
        print(body)
        assert code == 200


    def check_vin(self,vin=None):

        url = self.url + '/api/v1/checkVin'
        data = {'vin':vin}
        code,body = self.do_post(url,data=data)
        self.assert_bm_msg(code,body)

    def get_QRcode(self,vin):
        data = {'vin':vin}
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
    os.environ['ENV'] = 'UAT'
    aid = '4614183'
    car = TencentCar(user='15330011918',password='000000',vin='LFVTEST1231231231',aid=aid,token=True)
    vin = 'LFVSOP2TEST000071'
    hashVin = '90B3C60DFB4A4D9C6D88874B62249ACC'
    # car.check_vin(vin)
    car.get_QRcode(vin)
    # car.send_poi_hu(hashVin)
    # car.unbind(uid,vin=vin)
    # car.get_info(uid,vin)
    # car.bind_callback(aid='4614963',vin='B0EEE94911E24DFA3D39B21BBFAE6506',wecar_id=None,action='abc')


