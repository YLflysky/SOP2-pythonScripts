from box.base import Base
import random

class EShop(Base):
    '''
    商城API
    '''
    def __init__(self,tenant):
        super().__init__(tenant)
        self.url = None

    def assert_msg(self, code, body):
        print(body)
        assert 200 == code
        assert body['status'] == 'SUCCEED'

    def get_spare_list(self,category,index=1,size=10,**kwargs):
        '''
        获取备件商城列表
        '''
        url = self.url + '/goods/search'
        param = {'pageIndex':index,'pageSize':size}
        data = {'categoryId':category,**kwargs}
        code,body = self.do_post(url,data,params=param)
        self.assert_msg(code,body)
        return body

    def get_category_id(self):
        '''
        获取备件商城一级分类id
        :return:
        '''
        url = self.url + '/goods/category'
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)
        id = body['data']
        id = random.choice(id)['id']
        return id

    def get_spare_detail(self,goods_id):
        '''
        获取备件详情API
        '''
        url = self.url + '/goods/details'
        param = {'goodsId':goods_id}
        code,body = self.do_get(url,param)
        self.assert_msg(code,body)

class PointsShop(EShop):
    '''
    积分商城API
    '''
    def __init__(self,tenant):
        super().__init__(tenant)
        if tenant == 'BM':
            self.url = self.read_conf('sop2_env.conf',self.env,'eshop_host')
        elif tenant == 'MA':
            self.env = 'UAT'
            self.gate = True
            self.url = self.read_conf('ma_env.conf', self.env, 'eshop_host')
            self.add_header(self.read_conf('ma_env.conf', self.env, 'token_host'))


class SpareShop(EShop):
    '''
    备件商城API
    '''
    def __init__(self,tenant):
        super().__init__(tenant)
        if tenant == 'BM':
            self.url = self.read_conf('sop2_env.conf',self.env,'eshop_host2')
        elif tenant == 'MA':
            self.env = 'UAT'
            self.gate = True
            self.url = self.read_conf('ma_env.conf', self.env, 'eshop_host2')
            self.add_header(self.read_conf('ma_env.conf', self.env, 'token_host'))

    def get_spare_detail(self,goods_id):
        raise NotImplementedError('备件商城无此接口')

    def get_category_id(self):
        '''
        备件商城一级分类id
        :return:
        '''
        url = self.url + '/goods/category'
        code, body = self.do_get(url, None)
        self.assert_msg(code, body)
        id = body['data']
        id = random.choice(id)['categoryId']
        return id


if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    shop = PointsShop('MA')
    category = shop.get_category_id()
    print(category)
    # shop.get_spare_list('all')
    # goods_id = shop.get_spare_list(category='all')
    # goods_id = goods_id['data'][0]['goodsId']
    # shop.get_spare_detail('be50bc34-1926-4648-bbf8-5ff3a5d8266f')

