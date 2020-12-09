import pytest
import allure
import os
import random
from eshop.spare import SpareShop
from eshop.smart_shop import SmartEShop

spare = SpareShop()
bm_shop = SmartEShop(tenant='BM')

@pytest.mark.eshop
@allure.suite('spare shop')
@allure.title('获取备件商城category')
def test_get_spare_category():
    '''
    测试获取备件商城category
    '''
    res = spare.get_category_id()
    assert res in ['all','1993','37','32','31','1994','927','790','2','1995','764','1']


@pytest.mark.eshop
@allure.suite('spare shop')
@allure.title('获取备件商城列表')
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
@allure.title('获取备件商城列表')
def test_get_spare_list_sort():
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
@allure.title('获取备件商城列表')
def test_get_spare_list_reverse():
    '''
    测试获取备件列表，测试倒序排序
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

@allure.suite('eshop')
@allure.title('智能设备商城底层获取一级类目')
@pytest.mark.eshop
def test_get_category_1():
    res = bm_shop.category('FIRST_LEVEL',0)
    assert len(res['data']) > 0
    first = []
    for d in res['data']:
        assert d['grade'] == 0
        first.append(d['name'])
    with allure.step('一级分类列表'):
        allure.attach(first,'list',attachment_type=allure.attachment_type.TEXT)


@allure.suite('eshop')
@allure.title('智能设备商城底层获取二级类目')
@pytest.mark.eshop
def test_get_category_2():
    res1 = bm_shop.category('FIRST_LEVEL',0)
    parent = random.choice(res1['data'])['id']
    res = bm_shop.category('TWO_LEVEL',parent)
    assert len(res['data']) > 0
    for d in res['data']:
        assert parent == d['parentId']
        assert d['grade'] == 1


@allure.suite('eshop')
@allure.title('智能设备商城底层获取三级类目')
@pytest.mark.eshop
def test_get_category_3():
    res1 = bm_shop.category('FIRST_LEVEL',0)
    parent = random.choice(res1['data'])['id']
    res2 = bm_shop.category('TWO_LEVEL',parent)
    parent = random.choice(res2['data'])['id']
    res = bm_shop.category('THREE_LEVEL',parent)
    assert len(res['data']) > 0
    for d in res['data']:
        assert parent == d['parentId']
        assert d['grade'] == 2


@allure.suite('eshop')
@allure.title('智能设备商城获取商品类目异常情况')
@pytest.mark.eshop
@pytest.mark.parametrize('data',[('FIRST_LEVEL',1),('TWO_LEVEL',999),('THREE_LEVEL',999)])
def test_category_wrong(data):
    res = bm_shop.category(data[0],data[1])
    if res['returnStatus'] == 'SUCCEED':
        assert len(res['data']) == 0
    else:
        assert res['errorMessage']

@allure.suite('eshop')
@allure.title('智能设备商城获取商品详情')
@pytest.mark.eshop
@pytest.mark.parametrize('sku',['100002099880','100004466546','7360341','5066434'])
def test_smart_eshop_detail(sku):
    res = bm_shop.goods_detail(sku)
    assert res['data']['skuId'] == sku