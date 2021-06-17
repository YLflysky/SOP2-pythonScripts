from box.base import Base
import random
from box.lk_logger import lk
import os

class EShop(Base):
    '''
    商城API
    '''
    def __init__(self):
        super().__init__()
        self.url = None

    def assert_msg(self, code, body):
        self.assert_bm_msg(code,body)

    def get_list(self,category,index=1,size=10,**kwargs):
        '''
        获取商城列表
        '''
        url = self.url + '/goods/search'
        param = {'pageIndex':index,'pageSize':size}
        data = {'categoryId':category,**kwargs}
        code,body = self.do_post(url,data,params=param)
        self.assert_msg(code,body)
        return body

    def get_category_id(self):
        '''
        获取商城一级分类id
        :return:
        '''
        url = self.url + '/goods/category'
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)
        id = body['data']
        id = random.choice(id)['id']
        return id

    def get_detail(self,goods_id):
        '''
        获取商品详情API
        '''
        url = self.url + '/goods/details'
        param = {'goodsId':goods_id}
        code,body = self.do_get(url,param)
        self.assert_msg(code,body)
        return body

class PointsShop(EShop):
    '''
    积分商城API
    '''
    def __init__(self,tenant,token,name='15330011918',password='000000',vin='LFVTEST1231231231',aid='4614183'):
        super().__init__()
        if tenant == 'BM':
            self.url = self.read_conf('sop2_env.conf',self.env,'eshop_host')
        elif tenant == 'MA':
            self.gate = True
            if os.getenv('ENV') not in ('PROD', 'PERF'):
                self.env = 'UAT'
            self.url = self.read_conf('ma_env.conf', self.env, 'base_url_back') + '/mosc-sop2-eshop/mos/eshop_bonus/api/v1'
        if token:
            lk.prt('开始获取token')
            self.add_header(self.read_conf('ma_env.conf', self.env, 'token_host'),name,password,vin)



class SpareShop(EShop):
    '''
    备件商城API
    '''
    def __init__(self,tenant,token,name='15330011918',password='000000',vin='LFVTEST1231231231',aid='4614183'):
        super().__init__()
        if tenant == 'BM':
            self.url = self.read_conf('sop2_env.conf',self.env,'eshop_host2')
        elif tenant == 'MA':
            self.gate = True
            if os.getenv('ENV') not in ('PROD', 'PERF'):
                self.env = 'UAT'
            self.url = self.read_conf('ma_env.conf', self.env, 'base_url_back') + '/mosc-sop2-eshop/mos/eshop_spare/api/v1'
        if token:
            lk.prt('开始获取token')
            self.add_header(self.read_conf('ma_env.conf', self.env, 'token_host'),name,password,vin)


    def get_detail(self,goods_id):
        raise NotImplementedError('备件商城无此接口')


    def get_category_id(self):
        '''
        获取商城一级分类id
        :return:
        '''
        url = self.url + '/goods/category'
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)
        id = body['data']
        id = random.choice(id)['categoryId']
        return id



if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    # shop = PointsShop('MA',token=True,name='13618079403',password='xyz2020',vin='LFVSOP2TESTLY0040')
    shop = PointsShop('MA',token=True)
    category = shop.get_category_id()
    # print(category)
    # shop.get_list('all',index=1,size=10,sort='asc',sortName='score')
    # goods_id = shop.get_list(category='all')
    # goods_id = goods_id['data'][0]['goodsId']
    # shop.get_detail('45813f7d-5985-4b37-9979-366d84fdaad8')

