import pytest
import allure
import os
from eshop.spare import SpareShop

os.environ['ENV'] = 'DEV'
os.environ['gate'] = 'false'

spare = SpareShop()


@pytest.mark.eshop
@allure.suite('spare shop')
@allure.story('get category id')
def test_get_spare_category():
    '''
    测试获取备件商城category
    '''
    res = spare.get_category_id()
    assert res in ['all','1993','37','32','31','1994','927','790','2','1995','764','1']


@pytest.mark.eshop
@allure.suite('spare shop')
@allure.story('get list')
def test_get_spare_list():
    '''
    测试获取备件列表
    '''
    category = spare.get_category_id()
    res = spare.get_spare_list(category=category,index=1,size=100)
    if res['total'] != 0:
        names = []
        for good in res['data']:
            assert 'score' in good.keys()
            assert 'applyNumber' in good.keys()
            names.append(good['goodsName'])
        with allure.step('goods'):
            allure.attach(str(names),'goods_name')

@pytest.mark.eshop
@allure.suite('spare shop')
@allure.story('get list')
def test_get_spare_list_02():
    '''
    测试获取备件列表，测试排序
    '''
    res = spare.get_spare_list(category='all',index=1,size=100,sort='asc',sortName='score')
    if res['total'] != 0:
        names = []
        for good in res['data']:
            assert 'score' in good.keys()
            assert 'applyNumber' in good.keys()
            names.append(good['score'])
        assert names[-1] >= names[0]
        with allure.step('goods'):
            allure.attach(str(names),'score')

@pytest.mark.eshop
@allure.suite('spare shop')
@allure.story('get list')
def test_get_spare_list_03():
    '''
    测试获取备件列表，测试排序，倒序排序
    '''
    res = spare.get_spare_list(category='all',index=1,size=100,sort='desc',sortName='score')
    if res['total'] != 0:
        names = []
        for good in res['data']:
            assert 'score' in good.keys()
            assert 'applyNumber' in good.keys()
            names.append(good['score'])
        assert names[0] >= names[-1]
        with allure.step('goods'):
            allure.attach(str(names),'score')