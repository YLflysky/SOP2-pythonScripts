from box.base import Base
from car.tencent_car import TencentCar
from box.lk_logger import lk
import os, sys


class Team(TencentCar):
    def __init__(self):
        super().__init__()
        if self.gate:
            self.url = self.read_conf('sop2_env.conf', self.env, 'hu_host') + '/test-access/tm'
        else:
            lk.prt('can not resolve local environment')
            sys.exit(-1)

    def position(self,name):
        url = self.url + '/mosc-group-driving-sop2/api/v1/groups/actions/report_position_info'
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
        self.assert_msg(code=c, body=b)

    def create_group(self,uid,vin):
        url = self.url + '/mosc-group-driving-sop2/api/v1/createGroup'
        data = {'accountId':uid,'vin':vin,'longitude':float(self.f.longitude()),'latitude':float(self.f.latitude()),}
        code,body = self.do_post(url,data)
        self.assert_msg(code,body)
        return body['data']

    def find_last_group(self,uid,vin):
        url = self.url + '/mosc-group-driving-sop2/api/v1/findLastGroup'
        data = {'vin':vin,'accountId':uid}
        code,body = self.do_post(url,data)
        self.assert_msg(code,body)
        return body['data']

    def join_team(self,accountId,vin,group_id,invite):
        url = self.url + '/mosc-group-driving-sop2/api/v1/joinGroup'
        data = {'accountId':accountId,'vin':vin,'longitude':float(self.f.longitude()),'latitude':float(self.f.latitude()),
                'invitePassword':invite,'groupId':group_id}
        code,body = self.do_post(url,data=data)
        self.assert_msg(code,body)






if __name__ == '__main__':
    os.environ['GATE'] = 'true'
    os.environ['ENV'] = 'UAT'
    t = Team()
    uid=1234567
    vin='0000'
    open_id = t.get_info(uid,vin)['weChatOpenId']
    print(open_id)
    # groupId = t.find_last_group(uid,vin)['groupId']
    # invite_pwd = t.find_last_group(uid,vin)['invitePassword']
    # t.join_team(accountId=uid,vin=vin,group_id=groupId,invite=invite_pwd)
    # t.position(name='sergio')
