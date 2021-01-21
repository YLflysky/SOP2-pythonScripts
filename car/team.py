from box.base import Base
from car.tencent_car import TencentCar
from box.lk_logger import lk
import os, sys


class Team(TencentCar):
    def __init__(self):
        super().__init__()

        self.hu_url = self.read_conf('ma_env.conf', self.env, 'hu_host')
        self.url =self.hu_url + '/mosc-group-driving-sop2'

    def position(self,name):
        url = self.url + '/api/v1/groups/actions/report_position_info'
        data = {
            "travelid": "5880329234961",
            "ownername": name,
            "passwd": "275166",
            "users": [
                {
                    "userid": "9350191",
                    "pos": "104.226589|30.555322|45",
                    "state": "0",
                    "nickname": name,
                    "headUrl": "https://thirdwx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJYZjswWaTAiboxJsP4vqGzUmbnlCiaMxVicPpoiamk1HTG4nzDl76OiczPf1vXCK3Xvib3ibZibzOnNANBLw/132",
                    "type": "1"
                }
            ],
            "ver": "1",
            "target": {
                "pos": "104.226589|30.555322",
                "tname": "龙泉驿区一汽大众汽车有限公司成都分公司",
                "taddr": "四川省成都市龙泉驿区世纪大道",
                "userid": "9350191",
                "nickname": name,
                "headUrl": "https://wx.qlogo.cn/mmopen/vi_32/Q0j4TwGTfTJicysYuTY4KwphF7RVntmMak36yyTUfujOIibfia0AINhkT16ZNQm08ttyYOCG2c8cqE3doIeYogwXw/132"
            }
        }
        c, b = self.do_post(url, data=data)
        self.assert_ma_msg(code=c, body=b)

    def create_group(self,uid,vin):
        url = self.url + '/api/v1/createGroup'
        data = {'accountId':uid,'vin':vin,'longitude':float(self.f.longitude()),'latitude':float(self.f.latitude()),}
        code,body = self.do_post(url,data)
        self.assert_ma_msg(code,body)
        return body['data']

    def find_last_group(self,uid,vin):
        url = self.url + '/api/v1/findLastGroup'
        data = {'vin':vin,'accountId':uid}
        code,body = self.do_post(url,data)
        self.assert_msg(code,body)
        return body['data']

    def join_team(self,accountId,vin,group_id,invite):
        url = self.url + '/api/v1/joinGroup'
        data = {'accountId':accountId,'vin':vin,'longitude':float(self.f.longitude()),'latitude':float(self.f.latitude()),
                'invitePassword':invite,'groupId':group_id}
        code,body = self.do_post(url,data=data)
        self.assert_msg(code,body)

    def join_last_group(self,account,vin,group,longitude,latitude):
        '''
        加入最近一次组队
        :param account:
        :param vin:
        :param group:
        :param longtitude:
        :param latitude:
        :return:
        '''

        url = self.url + '/api/v1/joinLastGroup'

        data = {'accountId':account,'vin':vin,'groupId':group,'longitude':longitude,'latitude':latitude}

        c,b = self.do_post(url,data)
        self.assert_ma_msg(c,b)

    def get_hash_vin(self,vin):
        '''
        根据vin 获取 hash vin
        :param vin:
        :return:
        '''
        url = self.hu_url + '/vehicle/vehicleCustomerExpand/getEncryptionVinByVin'
        data = {'vin':vin}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)





if __name__ == '__main__':
    t = Team()
    uid='9349628'
    vin='LFVSOP2TEST000007'
    t.get_hash_vin(vin='LFVSOP2TESTLY0002')
    # t.create_group(uid,vin)
    # open_id = t.get_info(uid,vin)['weChatOpenId']
    # print(open_id)
    # groupId = t.find_last_group(uid,vin)['groupId']
    # invite_pwd = t.find_last_group(uid,vin)['invitePassword']
    # t.join_team(accountId=uid,vin=vin,group_id=groupId,invite=invite_pwd)
    t.join_last_group(account='9349829',group='5728304453166',longitude='116.388729',latitude='39.871198',vin='LFVSOP2TEST000048')
    # t.position(name='sergio')
