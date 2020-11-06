import pytest
import allure
from order.bm_order import BMOrder
import random
import json



bm = BMOrder()


def setup_module():
    bm.reload_config()

@pytest.mark.order
@allure.suite('order')
@allure.feature('BM车机端获取订单数量')
@pytest.mark.parametrize('uid', ('4614907', '1600841231973', '221', '11223344', '4614931'))
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
@allure.feature('BM车机端获取订单数量')
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
@allure.feature('BM车机端获取订单数量')
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
@allure.feature('BM车机端获取订单数量')
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
            'select count(1) as c from `order` where aid="221" and order_status in ("WAITING_PAY") and del_flag=0',
            'order')
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
            'select count(1) as c from `order` where aid="221" and order_status in ("CANCEL","EXPIRE") and del_flag=0',
            'order')
    elif status == '1005':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in ("REFUND_SUCCESS","REFUNDING") and del_flag=0',
            'order')
    else:
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status !="INIT" and del_flag=0 ',
            'order')

    assert sql_res[0]['c'] == int(count)


@allure.suite('order')
@allure.feature('BM车机端获取订单数量')
@pytest.mark.order
@pytest.mark.parametrize('category', ['00','01', '02'])
def test_order_count_05(category):
    '''
    根据category查询订单数量
    '''
    uid = '4614907'
    vin = bm.f.pyint()
    bm.reload_config()
    res = bm.order_count(vin, uid, orderCategory=category)
    assert res['description'] == '成功'
    count = res['data']
    order_category = bm.do_mysql_select(
        'select category from category_relation where hu_category = "{}"'.format(category), 'order')
    categories = []
    for c in order_category:
        categories.append(c['category'])
    sql = 'select count(1) as c from `order` where aid="4614907" and category in ("{}")'.format('","'.join(categories))
    sql_res = bm.do_mysql_select(sql, 'order')

    assert sql_res[0]['c'] == int(count)


@allure.suite('order')
@allure.feature('BM车机端获取订单数量')
@pytest.mark.order
def test_order_count_06():
    '''
    输入BM订单中不存在的status，报错
    '''
    uid = '4614907'
    vin = bm.f.pyint()
    status = bm.f.word()
    res = bm.order_count(vin, uid, orderStatus=status)
    assert res['description'] == 'AOD0103:ORDER_STATUS_INVALID'


@allure.suite('order')
@allure.feature('BM同步订单信息')
@pytest.mark.order
@pytest.mark.parametrize('brand',['VW','JETTA','AUDI'],ids=['brand为VW','brand为JETTA','brand为AUDI'])
def test_sync_bm_order(brand):
    '''
    测试同步BM适配层订单
    '''
    id = bm.f.pyint()
    vin = bm.f.pyint()
    ext_info = bm.f.pydict(4, True, value_types=str)
    discount_amount = '10000'
    order_amount = bm.f.pyint(10086, 100000)
    category = '111'
    sp_id = '111'
    service_id = 'CAR_WASH'
    title = bm.f.sentence()
    user_id = '123'
    status = 'INIT'
    status_desc = 'jojo'
    data = {'vin': vin, 'brand': brand, 'businessExtInfo': ext_info, 'discountAmount': discount_amount,
            'orderAmount': order_amount,
            'orderCategory': category, 'spId': sp_id, 'serviceId': service_id, 'title': title, 'userId': user_id,
            'serviceOrderState': status, 'serviceOrderStateDesc': status_desc}

    res = bm.sync_bm_order(id, data)
    try:
        assert res['description'] == '成功'
        order_no = res['data']
        sql_res = bm.do_mysql_select('select * from `order` where order_no="{}"'.format(order_no), 'order')
        assert sql_res[0]['total_amount'] == float(order_amount / 100)
        assert sql_res[0]['discount_amount'] == 100.00
        assert sql_res[0]['ex_order_no'] == str(id)
        assert sql_res[0]['brand'] == brand
    finally:
        bm.do_mysql_exec(
            'delete from order_detail where order_id =(select id from `order` where order_no="{}")'.format(order_no),
            'order')
        bm.do_mysql_exec('delete from `order` where order_no="{}" and aid="{}"'.format(order_no,user_id), 'order')


@allure.suite('order')
@allure.feature('BM适配层更新订单')
@pytest.mark.order
@pytest.mark.parametrize('d',[('INIT','jojo'),(None,None),('PROCESSING','kaka')])
def test_update_bm_order(d):
    '''
    测试BM适配层更新订单接口
    '''
    order = bm.do_mysql_select(' SELECT * FROM `order` WHERE origin="BM" and vin is not null and del_flag=0', 'order')
    order = random.choice(order)
    order_no = order['order_no']
    vin = order['vin']
    uid = order['aid']
    businessInfo = bm.f.pydict(4, True, value_types=str)
    businessState = d[0]
    businessStateDesc = d[1]
    event = bm.f.sentence()

    bm.update_bm_order(order_no, vin, uid, '1', businessExtInfo=businessInfo, businessState=businessState,
                       businessStateDesc=businessStateDesc,orderEvent = event)
    sql_res = bm.do_mysql_select('SELECT * FROM `order` WHERE order_no="{}"'.format(order_no), 'order')
    if d[0] is not None and d[1] is not None:
        assert sql_res[0]['business_status'] == businessState
        assert sql_res[0]['business_status_desc'] == businessStateDesc
    order_id = sql_res[0]['id']
    sql_res_detail = bm.do_mysql_select('select detail from order_detail where order_id={}'.format(order_id),'order')
    assert len(sql_res_detail) == 1


@allure.suite('order')
@allure.feature('BM车机端获取订单详情')
@pytest.mark.order
@pytest.mark.parametrize('d',[('221','29515778243258532831'),('33','20201104165745583380928'),('4612472','4612472112221')])
def test_bm_order_detail(d):
    res = bm.bm_order_detail(d[0],d[1],bm.random_vin())
    assert res['data']['orderCategory']
