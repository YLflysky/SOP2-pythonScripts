from ma_api.tencent_car import TencentCar
from box.utils import read_yml

class Team(TencentCar):
    def __init__(self,aid,user,password,vin,token=True):
        super().__init__(aid,user,password,vin,token)
        self.hu_url = self.read_conf('ma_env.conf', self.env, 'hu_host')
        self.url =self.hu_url + '/mosc-group-driving-sop2'

    def create_group(self,vin):
        url = self.url + '/api/v1/createGroup'
        data = {'vin':vin,'longitude':float(self.f.longitude()),'latitude':float(self.f.latitude())}
        code,body = self.do_post(url,data)
        self.assert_ma_msg(code,body)
        return body['data']

    def find_last_group(self,uid,vin):
        url = self.url + '/api/v1/findLastGroup'
        data = {'vin':vin,'accountId':uid}
        code,body = self.do_post(url,data)
        self.assert_bm_msg(code,body)
        return body['data']

    def join_team(self,vin,group_id,invite):
        url = self.url + '/api/v1/joinGroup'
        data = {'vin':vin,'longitude':float(self.f.longitude()),'latitude':float(self.f.latitude()),
                'invitePassword':invite,'groupId':group_id}
        code,body = self.do_post(url,data=data)
        self.assert_bm_msg(code,body)

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

    def get_trip_info(self,aid,vin):
        '''
        查询当前组队信息
        :param aid:
        :param vin:
        :return:
        '''
        url = self.url + '/api/v1/groups/actions/query_current'
        data = {'accountId':aid,'vin':vin}
        c,b = self.do_get(url,data)
        self.assert_ma_msg(c,b)

    def leave_group(self,vin,group,open_id,wecar_id):
        '''
        离开组队
        :param aid:
        :param vin:
        :param group:
        :param open_id:
        :param wecar_id:
        :return:
        '''
        url = self.url + '/api/v1/leaveGroup'
        data = {'vin':vin,'groupId':group,'wechatOpenId':open_id,'weCarId':wecar_id}
        c,b = self.do_post(url,data)
        self.assert_ma_msg(c,b)


if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'UAT'
    user_info =read_yml("../conf/user.yml")
    user_info = user_info['sergio']
    vin = user_info['vin']
    aid = user_info['aid']
    t = Team(user=user_info['user'],password=user_info['password'],vin=vin,aid=aid,token=True)
    # t.get_hash_vin(vin='LFVSOP2TESTLY0002')
    t.create_group(vin)
    # t.leave_group(vin=vin,group='151861669744099',open_id='1101503',wecar_id=1)
    # open_id = t.get_info(uid,vin)['weChatOpenId']
    # print(open_id)
    # groupId = t.find_last_group(uid=aid,vin=vin)['groupId']
    # invite_pwd = t.find_last_group(uid,vin1)['invitePassword']
    t.join_team(vin=vin,group_id='58801695237333',invite='235289')
    # t.get_trip_info(aid='9350160',vin='LFV3A23C4L3137420')
    # t.join_last_group(account='9349628',group='12345',longitude='116.388729',latitude='39.871198',vin='LFVSOP2TEST000007')

