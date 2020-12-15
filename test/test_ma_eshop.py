import pytest
import allure
import os
import random
from eshop.smart_shop import SmartEShop

ma_shop = SmartEShop(tenant='MA')


@allure.suite('ma-eshop')
@allure.title('MA智能设备商城底层获取一级类目')
@pytest.mark.eshop
def test_get_category_1():
    res = ma_shop.category()
    assert len(res['data']) > 0
    first = []
    for d in res['data']:
        assert d['grade'] == 0
        first.append(d['name'])
    with allure.step('一级分类列表'):
        allure.attach(first,'list',attachment_type=allure.attachment_type.TEXT)


@allure.suite('ma-eshop')
@allure.title('MA智能设备商城底层获取二级类目')
@pytest.mark.eshop
def test_get_category_2():
    res1 = ma_shop.category()
    parent = random.choice(res1['data'])['id']
    res = ma_shop.category2(parent)
    assert len(res['data']) > 0
    for d in res['data']:
        assert parent == d['parentId']
        assert d['grade'] == 1


@allure.suite('ma-eshop')
@allure.title('MA智能设备商城底层获取三级类目')
@pytest.mark.eshop
def test_get_category_3():
    res1 = ma_shop.category()
    parent = random.choice(res1['data'])['id']
    res2 = ma_shop.category2(parent)
    parent = random.choice(res2['data'])['id']
    res = ma_shop.category3(parent)
    assert len(res['data']) > 0
    for d in res['data']:
        assert parent == d['parentId']
        assert d['grade'] == 2


@allure.suite('ma-eshop')
@allure.title('MA智能设备商城获取商品详情')
@pytest.mark.eshop
@pytest.mark.parametrize('sku',['100002099880','100004466546','7360341','5066434'])
def test_smart_eshop_detail(sku):
    cp = ma_shop.f.word()
    res = ma_shop.goods_detail(sku,cp)
    assert res['data']['skuId'] == sku
    assert res['data']['cpId'] == cp


@allure.suite('ma-eshop')
@allure.title('MA智能设备商城获取商品列表，根据价格排序')
@pytest.mark.eshop
@pytest.mark.parametrize('sort',['desc','asc'])
def test_smart_eshop_list_01(sort):

    res = ma_shop.goods_list(no=1,size=10,sortName='price',sort=sort)
    prices = []
    for x in res['data']:
        prices.append(x['price'])
    print(prices)


@allure.suite('ma-eshop')
@allure.title('MA智能设备商城获取商品列表，根据关键字查询')
@pytest.mark.eshop
@pytest.mark.parametrize('key',['京','京鱼座音箱'])
def test_smart_eshop_list_02(key):

    res = ma_shop.goods_list(no=1,size=10,keyword=key)
    assert res['total'] == len(res['data'])
    for x in res['data']:
        assert key in x['skuName']


@allure.suite('ma-eshop')
@allure.title('MA智能设备商城获取商品列表，根据category2查询')
@pytest.mark.eshop
@pytest.mark.parametrize('category2',[12345,738,828,794])
def test_smart_eshop_list_03(category2):

    res = ma_shop.goods_list(no=1,size=10,category2Id=category2)
    assert res['total'] == len(res['data']) != 0


@allure.suite('ma-eshop')
@allure.title('MA智能设备商城获取商品列表，根据category3查询')
@pytest.mark.eshop
@pytest.mark.parametrize('category3',[[842,758,967,870]])
def test_smart_eshop_list_04(category3):
    res = ma_shop.goods_list(no=1,size=10,category3Ids=category3)
    assert res['total'] == len(res['data'])


@allure.suite('ma-eshop')
@allure.title('MA智能设备商城获取商品列表，同时传入category2和category3，报错')
@pytest.mark.eshop
def test_smart_eshop_list_05():
    res = ma_shop.goods_list(no=1,size=10,category3Ids=[967],category2Id=1276)
    assert res['errorMessage'] == 'ASE0002:二三分类同时存在'




