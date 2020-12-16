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
    res = bm_shop.category()
    assert len(res['data']) > 0
    first = []
    for d in res['data']:
        assert d['id']
        assert d['name']
        first.append(d['name'])
    with allure.step('一级分类列表'):
        allure.attach(str(first),'list',attachment_type=allure.attachment_type.TEXT)


@allure.suite('eshop')
@allure.title('智能设备商城底层获取二级类目')
@pytest.mark.eshop
def test_get_category_2():
    res = bm_shop.category2()
    assert len(res['data']) > 0
    for d in res['data']:
        assert d['id']
        assert d['name']


@allure.suite('eshop')
@allure.title('智能设备商城底层获取三级类目')
@pytest.mark.eshop
def test_get_category_3():
    res2 = bm_shop.category2()
    parent = random.choice(res2['data'])['id']
    res = bm_shop.category3(parent)
    assert len(res['data']) > 0
    for d in res['data']:
        assert d['id']
        assert d['name']


@allure.suite('eshop')
@allure.title('智能设备商城获取商品详情')
@pytest.mark.eshop
@pytest.mark.parametrize('sku',['100002099880','100004466546','7360341','5066434'])
def test_smart_eshop_detail(sku):
    cp = bm_shop.f.word()
    res = bm_shop.goods_detail(sku,cp)
    assert res['data']['skuId'] == sku
    assert res['data']['cpId'] == cp


@allure.suite('eshop')
@allure.title('智能设备商城获取商品列表，根据价格排序')
@pytest.mark.eshop
@pytest.mark.parametrize('sort',['desc','asc'])
def test_smart_eshop_list_01(sort):

    res = bm_shop.goods_list(no=1,size=10,sortName='price',sort=sort)
    prices = []
    for x in res['data']:
        prices.append(x['price'])
    print(prices)


@allure.suite('eshop')
@allure.title('智能设备商城获取商品列表，根据关键字查询')
@pytest.mark.eshop
@pytest.mark.parametrize('key',['京','京鱼座音箱'])
def test_smart_eshop_list_02(key):

    res = bm_shop.goods_list(no=1,size=10,keyword=key)
    assert res['totalCount'] == len(res['data'])
    for x in res['data']:
        assert key in x['skuName']


@allure.suite('eshop')
@allure.title('智能设备商城获取商品列表，根据category2查询')
@pytest.mark.eshop
@pytest.mark.parametrize('category2',[12345,738,828,794])
def test_smart_eshop_list_03(category2):

    res = bm_shop.goods_list(no=1,size=10,category2Id=category2)
    assert res['totalCount'] == len(res['data']) != 0


@allure.suite('eshop')
@allure.title('智能设备商城获取商品列表，根据category3查询')
@pytest.mark.eshop
@pytest.mark.parametrize('category3',[[842,758,967,870]])
def test_smart_eshop_list_04(category3):

    res = bm_shop.goods_list(no=1,size=10,category3Ids=category3)
    assert res['totalCount'] == len(res['data']) == 4


@allure.suite('eshop')
@allure.title('智能设备商城获取商品列表，同时传入category2和category3，报错')
@pytest.mark.eshop
def test_smart_eshop_list_04():
    res = bm_shop.goods_list(no=1,size=10,category3Ids=[967],category2Id=1276)
    assert res['totalCount'] == len(res['data'])




