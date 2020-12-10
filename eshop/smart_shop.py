from box.base import Base
import os,sys


class SmartEShop(Base):

    def __init__(self,tenant):
        super().__init__()
        if tenant == 'BM':
            self.url = self.read_conf('sop2_env.conf',self.env,'smart_eshop_host')
        elif tenant == 'MA':
            self.url = self.read_conf('ma_env.conf', self.env, 'host')
        else:
            print('no such tenant...')
            sys.exit(-1)

    def category(self,category_type,parent_id):
        '''
        商品类目查询
        :return:
        '''
        url = self.url + '/public/v1/smart4jd/search/category'
        data = {'categoryType':category_type,'parentId':parent_id}
        c,b = self.do_get(url,data)
        self.assert_msg(c,b)
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
        data = {'pageNo':no,'pageSize':size,**kwargs}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)

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


if __name__ == '__main__':

    os.environ['GATE'] = 'true'
    os.environ['ENV'] = 'SIT'
    shop = SmartEShop(tenant='BM')
    # shop.category(category_type='FIRST_LEVEL',parent_id=0)
    # shop.goods_list(keyword='京')
    shop.goods_detail(sku_id=100004466546,cp_id='123')