from order.tsp_order import TSPOrder
import pytest
import allure
import random

tsp = TSPOrder()


@allure.suite('tsp_order')
@allure.title('tsp获取订单列表，不传筛选条件，查询所有订单')
@pytest.mark.tsp_order
def test_tsp_list_01():
    '''
    测试tsp获取全部订单
    :return:
    '''
    res = tsp.order_list()
    sql_res = tsp.do_mysql_select('SELECT COUNT(1) as total from `order` where del_flag=0','fawvw_order')
    assert res['totalCount'] == sql_res[0]['total']
    data = random.choice(res['data'])
    assert data['orderCategory']
    assert data['origin']
    assert data['title']
    assert data['orderNo']
    assert data['exOrderNo']
    assert data['actualPayAmount']
    assert data['orderStatus']
    assert data['createTime']

@allure.suite('tsp_order')
@allure.title('tsp获取订单列表，传入开始结束时间')
@pytest.mark.tsp_order
def test_tsp_list_02():
    '''
    测试tsp获取订单，筛选条件为时间
    :return:
    '''
    st = tsp.time_delta(days=-10)
    et = tsp.time_delta(days=-5)
    res = tsp.order_list(startTime=st,endTime=et,size=10,no=1)
    data = random.choice(res['data'])
    assert data['orderCategory']
    assert data['origin']
    assert data['title']
    assert data['orderNo']
    assert data['exOrderNo']
    assert 'actualPayAmount' in data.keys()
    assert data['orderStatus']
    assert st <= data['createTime'] <= et


@allure.suite('tsp_order')
@allure.title('tsp获取订单列表，传入orderCategoryList')
@pytest.mark.tsp_order
@pytest.mark.parametrize('category',['102','110','111'],ids=['VPA订单','音乐VIP订单','流量订单'])
def test_tsp_list_03(category):
    '''
    测试tsp获取订单，筛选条件为orderCategoryList
    :return:
    '''

    res = tsp.order_list(orderCategoryList=[category],size=10,no=2)
    data = random.choice(res['data'])
    assert data['orderCategory'] == category
    assert data['origin']
    assert 'title' in data.keys()
    assert data['orderNo']
    assert data['exOrderNo']
    assert 'actualPayAmount' in data.keys()
    assert data['orderStatus']
    assert data['createTime']

@allure.suite('tsp_order')
@allure.title('tsp获取订单列表，传入orderStatusList')
@pytest.mark.tsp_order
def test_tsp_list_04():
    '''
    测试tsp获取订单，筛选条件为orderStatusList
    :return:
    '''

    res = tsp.order_list(orderStatusList=['WAITING_PAY'],size=10,no=2)
    data = random.choice(res['data'])
    assert data['orderCategory']
    assert data['origin']
    assert 'title' in data.keys()
    assert data['orderNo']
    assert data['exOrderNo']
    assert 'actualPayAmount' in data.keys()
    assert data['orderStatus'] == 'WAITING_PAY'
    assert data['createTime']


@allure.suite('tsp_order')
@allure.title('tsp获取订单列表，传入orderNo模糊查询')
@pytest.mark.tsp_order
@pytest.mark.parametrize('no',['ftb','2020','ftb20201202111244868753664','2020092406063019761440'])
def test_tsp_list_05(no):
    '''
    测试tsp获取订单，筛选条件为orderNo模糊查询
    :return:
    '''

    res = tsp.order_list(orderNo=no,size=10,no=1)
    data = random.choice(res['data'])
    assert data['orderCategory']
    assert data['origin']
    assert 'title' in data.keys()
    assert no in data['orderNo']
    assert data['exOrderNo']
    assert 'actualPayAmount' in data.keys()
    assert data['orderStatus']
    assert data['createTime']


@allure.suite('tsp_order')
@allure.title('tsp获取订单列表，传入exOrderNo模糊查询')
@pytest.mark.tsp_order
@pytest.mark.parametrize('no',['2020','2020092406063019761440','cd49a4f31f4f4593af4de6298348fdbc'])
def test_tsp_list_06(no):
    '''
    测试tsp获取订单，筛选条件为exOrderNo模糊查询
    :return:
    '''

    res = tsp.order_list(exOrderNo=no,size=10,no=1)
    data = random.choice(res['data'])
    assert data['orderCategory']
    assert data['origin']
    assert 'title' in data.keys()
    assert data['orderNo']
    assert no in data['exOrderNo']
    assert 'actualPayAmount' in data.keys()
    assert data['orderStatus']
    assert data['createTime']