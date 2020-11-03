from box.base import Base
import random

class SpareShop(Base):
    '''
    备件商城API
    '''
    def __init__(self):
        super().__init__()

        self.url = self.read_conf('sop2_env.conf',self.env,'be_host')

    def get_spare_list(self,category,index,size,**kwargs):
        '''
        获取备件商城列表
        '''
        url = self.url + '/eshop/mos/eshop_bonus/api/v1/goods/search'
        param = {'pageIndex':index,'pageSize':size}
        data = {'categoryId':category,**kwargs}
        code,body = self.do_post(url,data,params=param)
        self.assert_msg(code,body)
        return body

    def get_category_id(self):
        url = self.url + '/eshop/mos/eshop_bonus/api/v1/goods/category'
        code,body = self.do_get(url,None)
        self.assert_msg(code,body)
        id = body['data']
        id = random.choice(id)['id']
        return id

    def get_spare_detail(self,goods_id):
        '''
        获取备件详情API
        '''
        url = self.url + '/eshop/mos/eshop_bonus/api/v1/goods/details'
        param = {'goodsId':goods_id}
        code,body = self.do_get(url,param)
        self.assert_msg(code,body)


    def assert_msg(self, code, body):
        print(body)
        assert 200 == code
        assert body['status'] == 'SUCCEED'

if __name__ == '__main__':
    import os
    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'DEV'
    shop = SpareShop()
    category = shop.get_category_id()
    # print(category)
    # goods_id = shop.get_spare_list(category='all',index=10,size=20)
    # goods_id = goods_id['data'][0]['goodsId']
    shop.get_spare_detail('be50bc34-1926-4648-bbf8-5ff3a5d8266f')

