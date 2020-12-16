from box.base import Base
import os,sys


class SmartEShop(Base):

    def __init__(self,tenant):
        super().__init__()
        self.tenant = tenant
        if tenant == 'BM':
            self.url = self.read_conf('sop2_env.conf',self.env,'smart_eshop_host')
        elif tenant == 'MA':
            self.env= 'UAT'
            self.gate = True
            self.url = self.read_conf('ma_env.conf', self.env, 'eshop_host')
            self.add_header()
        else:
            print('no such tenant...')
            sys.exit(-1)

    def assert_msg(self, code, body):
        print(body)
        assert 200 == code


    def category(self):
        '''
        商品类目查询
        :return:
        '''

        url = self.url + '/public/v1/smart4jd/search/category'
        c,b = self.do_get(url,None)
        self.assert_msg(c,b)
        return b

    def category2(self,parentId):
        '''
        商品二级类目查询
        :param parentId: 一级类目id
        :return:
        '''
        url = self.url + '/public/v1/smart4jd/search/category2'
        data = {'category1ID':parentId}
        c, b = self.do_get(url, data)
        self.assert_msg(c, b)
        return b

    def category3(self,parentId):
        '''
        商品二级类目查询
        :param parentId: 二级类目id
        :return:
        '''

        url = self.url + '/public/v1/smart4jd/search/category3'
        data = {'category2ID':parentId}
        c, b = self.do_get(url, data)
        self.assert_msg(c, b)
        return b

    def goods_list(self,no=1,size=5,**kwargs):
        '''
        商品列表查询
        :param no: 当前页数
        :param size: 当前条数
        :param kwargs:
        :return:
        '''
        url = self.url + '/public/v1/smart4jd/search/list'
        data = {**kwargs}
        params = {'pageNo':no,'pageSize':size}
        c,b = self.do_post(url,data,params)
        self.assert_msg(c,b)
        return b

    def goods_detail(self,sku_id,cp_id=None):
        '''
        根据sku_id查询商品详情
        :param sku_id:
        :param cp_id:
        :return:
        '''
        url = self.url + '/public/v1/smart4jd/search/details'
        data = {'skuId':sku_id,'cpId':cp_id}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def refresh_category_and_goods_detail(self):
        '''
        清除商品缓存信息接口
        :return:
        '''
        url = self.url + '/public/v1/oss/manage/refresh_category_and_prod_detail'
        c,b = self.do_get(url,None)
        self.assert_msg(c,b)


if __name__ == '__main__':

    os.environ['GATE'] = 'false'
    os.environ['ENV'] = 'UAT'
    shop = SmartEShop(tenant='MA')
    # shop.refresh_category_and_goods_detail()
    shop.category()
    # shop.category2(737)
    # shop.category3(14015)
    # shop.goods_list(no=1,size=2)
    # shop.goods_detail(sku_id=100004466546,cp_id='123')