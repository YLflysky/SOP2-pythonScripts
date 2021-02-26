from ma_api.tencent_car import TencentCar


class Team(TencentCar):
    def __init__(self):
        super().__init__()
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




if __name__ == '__main__':
    import os
    os.environ['ENV'] = 'UAT'
    t = Team()
    uid='4614183'
    vin='LFVTEST1231231231'
    t.get_hash_vin(vin='LFVSOP2TESTLY0002')
    # t.create_group(uid,vin)
    # open_id = t.get_info(uid,vin)['weChatOpenId']
    # print(open_id)
    # groupId = t.find_last_group(uid,vin)['groupId']
    # invite_pwd = t.find_last_group(uid,vin)['invitePassword']
    # t.join_team(accountId=uid,vin=vin,group_id='53011910083707',invite=invite_pwd)
    # t.join_last_group(account=uid,group='588079202560',longitude='116.388729',latitude='39.871198',vin=vin)

