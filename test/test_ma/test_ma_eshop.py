import pytest
import allure
import os
import random
from eshop.eshop import SpareShop,PointsShop

bonus = PointsShop(tenant='MA')
spare = SpareShop('MA')


@pytest.mark.ma_eshop
@allure.suite('ma bonus shop')
@allure.title('获取积分商城category')
def test_get_bonus_category():
    '''
    测试获取积分商城category
    '''
    res = bonus.get_category_id()
    assert res


@pytest.mark.eshop
@allure.suite('ma bonus shop')
@allure.title('获取积分商城列表')
def test_get_bonus_list():
    '''
    测试获取积分列表
    '''
    category = bonus.get_category_id()
    res = bonus.get_list(category=category,index=1,size=100)
    if res['total'] != 0:
        names = []
        for good in res['data']:
            assert 'mainPhoto' in good.keys()
            assert good['score']
            names.append(good['goodsName'])
        with allure.step('goods'):
            allure.attach(str(names),'goods_name')

@pytest.mark.ma_eshop
@allure.suite('ma bonus shop')
@allure.title('MA获取积分商城列表>>goodsUrl格式测试')
def test_get_bonus_list_url():
    '''
    测试获取积分列表
    '''
    res = bonus.get_list(category='all',index=1,size=100)
    if res['total'] != 0:
        for good in res['data']:
            goods_url = good['goodsUrl']
            base_url = goods_url.split('=')
            # assert base_url[0] == 'https://mall.faw-vw.com/shop-m/page/member/member-spike.html'
            assert base_url[1] == good['goodsId']

@pytest.mark.ma_eshop
@allure.suite('ma bonus shop')
@allure.title('获取积分商城列表>>积分从小到大')
def test_get_bonus_list_sort():
    '''
    测试获取积分列表，测试根据积分排序
    '''
    res = bonus.get_list(category='all',index=1,size=10,sort='asc',sortName='score')
    if res['total'] != 0:
        names = []
        for good in res['data']:
            assert good['score']
            names.append(good['score'])
        assert names[-1] >= names[0]
        with allure.step('goods'):
            allure.attach(str(names),'score')


@pytest.mark.ma_eshop
@allure.suite('ma bonus shop')
@allure.title('获取积分商城列表>>积分倒序')
def test_get_bonus_list_reverse():
    '''
    测试获取积分列表，测试倒序排序
    '''
    res = bonus.get_list(category='all',index=1,size=100,sort='desc',sortName='score')
    if res['total'] != 0:
        names = []
        for good in res['data']:
            assert 'score' in good.keys()
            names.append(good['score'])
        assert names[0] >= names[-1]
        with allure.step('goods'):
            allure.attach(str(names),'score')

@pytest.fixture()
def get_goods_id():
    res = bonus.get_list(category='all',size=1,index=10)
    return random.choice(res['data'])['goodsId']


@pytest.mark.ma_eshop
@allure.suite('ma bonus shop')
@allure.title('获取积分商城商品详情')
def test_bonus_detail(get_goods_id):
    res = bonus.get_detail(get_goods_id)
    assert res['data']['goodsName']
    assert res['data']['descriptionPhoto']
    assert res['data']['score']
    assert res['data']['goodsUrl']


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






