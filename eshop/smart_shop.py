from box.base import Base
import os,sys
from box.lk_logger import lk


class SmartEShop(Base):

    def __init__(self,tenant,token,name='15330011918',password='000000',vin='LFVTEST1231231231',aid='4614183'):
        super().__init__()
        if tenant == 'BM':
            self.url = self.read_conf('sop2_env.conf',self.env,'smart_eshop_host')
        elif tenant == 'MA':
            self.gate = True
            if os.getenv('ENV') not in ('PROD', 'PERF'):
                self.env = 'UAT'
            self.url = self.read_conf('ma_env.conf', self.env, 'base_url_hu') + '/mosc-dispatch/ep/eshop'
        else:
            print('no such tenant...')
            sys.exit(-1)
        if token:
            lk.prt('开始获取token')
            self.add_header(self.read_conf('ma_env.conf', self.env, 'token_host'),name,password,vin)

    def assert_msg(self, code, body):
        self.assert_bm_msg(code,body)


    def category(self):
        '''
        商品类目查询
        :return:
        '''

        url = self.url + '/public/v1/smart4jd/search/category'
        c,b = self.do_get(url,None)
        self.assert_msg(c,b)
        return b

    def category2(self):
        '''
        商品二级类目查询
        :param parentId: 一级类目id
        :return:
        '''
        url = self.url + '/public/v1/smart4jd/search/category2'
        c, b = self.do_get(url, None)
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
    os.environ['ENV'] = 'PROD'
    shop = SmartEShop(tenant='MA',token=True,name='13618079403',password='xyz2020',vin='LFVSOP2TESTLY0040')
    # shop.refresh_category_and_goods_detail()
    # shop.category()
    # shop.category2()
    # shop.category3(parentId=108000)
    # shop.goods_list(keywords='abcdiqdqw')
    shop.goods_list(categoryId=652,size=20)
    # shop.goods_detail(sku_id='123',cp_id='123')