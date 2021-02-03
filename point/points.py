from box.base import Base
import os



class Points(Base):
    def __init__(self,tenant='BM'):
        super().__init__(tenant)

        self.p_url = self.read_conf('sop2_env.conf',self.env,'integration_host')
        self.hu_url = self.read_conf('sop2_env.conf',self.env,'hu_host')

    def get_user_level(self,aid,system_key,tenant):
        '''
        积分底层获取用户等级
        :param aid: 大众用户id
        :param system_key:系统来源编号
        :param tenant:品牌
        :return:
        '''
        url = self.p_url + '/is/cdp/user/rights/level'
        data = {'aid':aid,'systemKey':system_key,'tenantId':tenant}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def bm_get_user_level(self,aid):
        '''
        BM车机端查询用户积分等级
        :param aid: 用户id
        :return:
        '''
        self.header['aid'] = aid
        url = self.hu_url + '/point/user/level'
        c,b = self.do_get(url,params=None)
        self.assert_bm_msg(c,b)
        return b

    def get_user_points(self,aid):
        '''
        底层获取用户积分信息
        :param aid:用户id
        :return:
        '''
        url = self.p_url + '/is/cdp/user/score/info'
        data = {'aid':aid}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def bm_get_user_points(self,aid):
        '''
        BM车机端获取用户积分信息接口
        :param aid: 用户id
        :return:
        '''
        self.header['aid'] = aid
        url = self.hu_url + '/point/user/score'
        c,b = self.do_get(url,None)
        self.assert_bm_msg(c,b)
        return b

    def get_points_stream(self,index,size,aid):
        '''
        底层获取积分流水
        :param index:当前页>=1
        :param size: 显示条数5≤x≤20
        :param aid: 用户id
        :return:
        '''
        data = {'pageIndex':index,'pageSize':size,'aid':aid}
        url = self.p_url + '/is/cdp/user/score/score_change'
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def bm_get_points_stream(self,aid,index=1,size=10):
        '''
        BM车机端获取用户积分流水
        :param index:当前页>=1
        :param size: 显示条数5≤x≤20
        :param aid: 用户id
        :return:
        '''

        data = {'pageIndex': index, 'pageSize': size}
        self.header['aid'] = aid
        url = self.hu_url + '/point/user/detail'
        c, b = self.do_get(url, data)
        self.assert_bm_msg(c, b)
        return b


if __name__ == '__main__':
    os.environ['ENV'] = 'UAT'
    os.environ['gate'] = 'false'
    p = Points()
    # p.get_user_level(aid='123',system_key='267C13173FE04A57AX',tenant='VW')
    # p.bm_get_user_level(aid='1234')
    # p.get_user_points(aid='9353750')
    p.bm_get_user_points(aid='9353750')
    # p.bm_get_points_stream(aid='123')
    # p.get_points_stream(index=1,size=10,aid='1234')