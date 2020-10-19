import pytest
import allure
import os
from order.bm_order import BMOrder

os.environ['ENV'] = 'DEV'
os.environ['GATE'] = 'false'

bm = BMOrder()


@pytest.mark.order
@allure.suite('order')
@allure.story('hu count')
@pytest.mark.parametrize('uid', ('4614907', '1600841231973', '221', '11223344', '哈哈jiu%%%'))
def test_order_count(uid):
    '''
    测试车机端根据vin和uid获取订单数量
    '''
    vin = bm.f.pyint()
    count = bm.order_count(vin, uid)['data']
    sql_res = bm.do_mysql_select('select count(1) as c from `order` where aid="{}" and del_flag=0'.format(uid), 'order')
    assert sql_res[0]['c'] == int(count)
    with allure.step('测试结果'):
        allure.attach('uid为{}的订单数量获取成功：{}'.format(uid, count), '测试结果')


@allure.suite('order')
@allure.story('hu count')
@pytest.mark.order
def test_order_count_fail():
    '''
    不输入uid
    '''
    vin = bm.f.pyint()
    uid = None
    res = bm.order_count(vin, uid)
    assert res['status'] == '400'


@allure.suite('order')
@allure.story('hu count')
@pytest.mark.order
def test_order_count_03():
    '''
    输入开始和结束时间
    '''
    uid = '4614907'
    vin = bm.f.pyint()
    begin = '2020-10-01 00:00:00'
    end = bm.time_delta()
    res = bm.order_count(vin, uid, beginTime=begin, endTime=end)
    assert res['description'] == '成功'
    count = res['data']
    sql_res = bm.do_mysql_select(
        'select count(1) as c from `order` where aid="{}" and create_date between "{}" and "{}"'.format(uid, begin,
                                                                                                        end), 'order')
    assert sql_res[0]['c'] == int(count)


@allure.suite('order')
@allure.story('hu count')
@pytest.mark.order
@pytest.mark.parametrize('status', ['1000', '1001', '1002', '1003', '1004', '1005'])
def test_order_count_04(status):
    '''
    输入订单状态
    '''
    uid = '221'
    vin = bm.f.pyint()
    res = bm.order_count(vin, uid, orderStatus=status)
    assert res['description'] == '成功'
    count = res['data']
    if status == '1001':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in ("WAITING_PAY") and del_flag=0', 'order')
    elif status == '1002':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in '
            '("PROCESSING","REFUND_FAILED","PAY_SUCCESS","PAY_FAILED","RESERVED") and del_flag=0',
            'order')
    elif status == '1003':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in ("FINISH") and del_flag=0', 'order')
    elif status == '1004':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in ("CANCEL","EXPIRE") and del_flag=0', 'order')
    elif status == '1005':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in ("REFUND_SUCCESS","REFUNDING") and del_flag=0', 'order')
    else:
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and del_flag=0 ',
            'order')

    assert sql_res[0]['c'] == int(count)


@allure.suite('order')
@allure.story('hu count')
@pytest.mark.order
def test_order_count_05():
    '''
    输入订单category为01
    '''
    uid = '4614907'
    vin = bm.f.pyint()
    bm.reload_config()
    res = bm.order_count(vin, uid, orderCategory='01')
    assert res['description'] == '成功'
    count = res['data']
    order_category = bm.do_mysql_select('select category from category_relation where hu_category="01"','order')
    order_category = order_category[0]['category']
    sql_res = bm.do_mysql_select('select count(1) as c from `order` where aid="4614907" and category="{}"'.format(order_category),'order')
    assert sql_res[0]['c'] == int(count)