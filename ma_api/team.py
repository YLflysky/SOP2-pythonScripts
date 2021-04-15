from ma_api.tencent_car import TencentCar


class Team(TencentCar):
    def __init__(self,aid,user,password,vin,token=True):
        super().__init__(aid,user,password,vin,token)
        self.hu_url = self.read_conf('ma_env.conf', self.env, 'hu_host')
        self.url =self.hu_url + '/mosc-group-driving-sop2'

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
        self.assert_bm_msg(code,body)
        return body['data']

    def join_team(self,accountId,vin,group_id,invite):
        url = self.url + '/api/v1/joinGroup'
        data = {'accountId':accountId,'vin':vin,'longitude':float(self.f.longitude()),'latitude':float(self.f.latitude()),
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

    def leave_group(self,aid,vin,group,open_id,wecar_id):
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
        data = {'vin':vin,'accountId':aid,'groupId':group,'wechatOpenId':open_id,'weCarId':wecar_id}
        c,b = self.do_post(url,data)
        self.assert_ma_msg(c,b)




if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'UAT'
    t = Team(user='15330011918',password='000000',vin='LFVTEST1231231231',aid='4614183',token=True)

    # t.get_hash_vin(vin='LFVSOP2TESTLY0002')
    # t.create_group('4613020','LFVSOP2TEST000401')
    t.leave_group(aid='4613020',vin='LFVSOP2TEST000401',group='1503674656412',open_id='1101503',wecar_id=1)
    # open_id = t.get_info(uid,vin)['weChatOpenId']
    # print(open_id)
    # groupId = t.find_last_group(uid,vin1)['groupId']
    # invite_pwd = t.find_last_group(uid,vin1)['invitePassword']
    # t.join_team(accountId='4614963',vin='LFVSOP2TESTLY0073',group_id='5880469272221',invite='660537')
    # t.get_trip_info('4613020','LFVSOP2TEST000401')
    # t.join_last_group(account=uid,group='588079202560',longitude='116.388729',latitude='39.871198',vin=vin)

