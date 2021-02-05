import pytest
import allure
import os
import random
from eshop.eshop import SpareShop


spare = SpareShop('MA')

@pytest.mark.ma_eshop
@allure.suite('ma spare shop')
@allure.title('获取备件商城category')
def test_get_spare_category():
    '''
    测试获取备件商城category
    '''
    res = spare.get_category_id()
    assert res


@pytest.mark.eshop
@allure.suite('ma spare shop')
@allure.title('获取备件商城列表')
def test_get_spare_list():
    '''
    测试获取备件列表
    '''
    category = spare.get_category_id()
    res = spare.get_list(category=category,index=1,size=100)
    if res['total'] != 0:
        names = []
        for good in res['data']:
            assert 'mainPhoto' in good.keys()
            assert good['price']
            assert 'promotionPrice' in good.keys()
            names.append(good['goodsName'])
        with allure.step('goods'):
            allure.attach(str(names),'goods_name')


@pytest.mark.ma_eshop
@allure.suite('ma spare shop')
@allure.title('获取备件商城列表>>价格从低到高')
def test_get_spare_list_sort():
    '''
    测试获取备件列表，测试根据价格排序
    '''
    res = spare.get_list(category='all',index=1,size=10,sort='asc',sortName='price')
    if res['total'] != 0:
        names = []
        for good in res['data']:
            assert good['price']
            names.append(good['price'])
        assert names[-1] >= names[0]
        with allure.step('goods'):
            allure.attach(str(names),'price')


@pytest.mark.ma_eshop
@allure.suite('ma spare shop')
@allure.title('获取备件商城列表>>价格倒序')
def test_get_spare_list_reverse():
    '''
    测试获取备件列表，测试倒序排序
    '''
    res = spare.get_list(category='all',index=1,size=100,sort='desc',sortName='price')
    if res['total'] != 0:
        names = []
        for good in res['data']:
            assert 'price' in good.keys()
            names.append(good['price'])
        assert names[0] >= names[-1]
        with allure.step('goods'):
            allure.attach(str(names),'price')