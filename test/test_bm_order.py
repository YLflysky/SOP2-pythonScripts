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
@allure.title('BM车机端获取订单数量')
@pytest.mark.parametrize('uid', ('4614907', '1600841231973', '221', '11223344', '4614931')
                         ,ids=['用户id=4614907','用户id=1600841231973','用户id=221','用户id=11223344','用户id=4614931'])
def test_order_count(uid):
    '''
    测试车机端根据vin和uid获取订单数量
    '''
    vin = bm.random_vin()
    count = bm.order_count(vin, uid)['data']
    sql_res = bm.do_mysql_select('select count(1) as c from `order` where aid="{}" and del_flag=0'.format(uid), 'fawvw_order')
    assert sql_res[0]['c'] == int(count)
    with allure.step('测试结果'):
        allure.attach('uid为{}的订单数量获取成功：{}'.format(uid, count), '测试结果')


@allure.suite('order')
@allure.title('BM车机端获取订单数量')
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
@allure.title('BM车机端获取订单数量')
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
                                                                                                        end), 'fawvw_order')
    assert sql_res[0]['c'] == int(count)


@allure.suite('order')
@allure.title('BM车机端获取订单数量')
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
            'fawvw_order')
    elif status == '1002':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in '
            '("PROCESSING","REFUND_FAILED","PAY_SUCCESS","PAY_FAILED","RESERVED") and del_flag=0',
            'fawvw_order')
    elif status == '1003':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in ("FINISH") and del_flag=0', 'fawvw_order')
    elif status == '1004':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in ("CANCEL","EXPIRE") and del_flag=0',
            'fawvw_order')
    elif status == '1005':
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status in ("REFUND_SUCCESS","REFUNDING") and del_flag=0',
            'fawvw_order')
    else:
        sql_res = bm.do_mysql_select(
            'select count(1) as c from `order` where aid="221" and order_status !="INIT" and del_flag=0 ',
            'fawvw_order')

    assert sql_res[0]['c'] == int(count)


@allure.suite('order')
@allure.title('BM车机端获取订单数量')
@pytest.mark.order
@pytest.mark.parametrize('category', ['00', '01', '02'])
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
        'select category from category_relation where hu_category = "{}"'.format(category), 'fawvw_order')
    categories = []
    for c in order_category:
        categories.append(c['category'])
    sql = 'select count(1) as c from `order` where aid="4614907" and category in ("{}")'.format('","'.join(categories))
    sql_res = bm.do_mysql_select(sql, 'fawvw_order')

    assert sql_res[0]['c'] == int(count)


@allure.suite('order')
@allure.title('BM车机端获取订单数量')
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
@allure.title('BM同步订单信息')
@pytest.mark.order
@pytest.mark.parametrize('info', [(107,'BIGBOX','CAR_WASH','VW'),
                                  (105,'FLEETIN','GAS','JETTA'),
                                  (104,'CN_BOOKING','HOTEL','AUDI')], ids=['洗车订单', '加油订单', '酒店订单'])
def test_sync_bm_order(info):
    '''
    测试同步BM适配层订单
    '''
    ex_order = bm.f.pyint()
    vin = bm.f.pyint()
    ext_info = bm.f.pydict(4, True, value_types=str)
    discount_amount = '10000'
    order_amount = bm.f.pyint(10086, 100000)
    title = bm.f.sentence()
    user_id = '123'
    status = 'INIT'
    status_desc = bm.f.word()
    create_time = bm.get_time_stamp()
    goods = bm.f.md5()
    data = {'vin': vin, 'brand': info[3], 'businessExtInfo': ext_info, 'discountAmount': discount_amount,
            'orderAmount': order_amount,'goodsId':goods,
            'orderCategory': info[0], 'spId': info[1], 'serviceId': info[2], 'title': title, 'userId': user_id,
            'serviceOrderState': status, 'serviceOrderStateDesc': status_desc,'createdTime':create_time}

    res = bm.sync_bm_order(ex_order, data)
    try:
        assert res['description'] == '成功'
        order_no = res['data']
        sql_res = bm.do_mysql_select('select * from `order` where order_no="{}"'.format(order_no), 'fawvw_order')
        assert sql_res[0]['total_amount'] == float(order_amount / 100)
        assert sql_res[0]['discount_amount'] == 100.00
        assert sql_res[0]['ex_order_no'] == str(ex_order)
        assert sql_res[0]['brand'] == info[3]
        assert sql_res[0]['sp_id'] == info[1]
        assert sql_res[0]['service_id'] == info[2]
        assert sql_res[0]['goods_id'] == goods
    finally:
        bm.do_mysql_exec(
            'delete from order_detail where order_id =(select id from `order` where order_no="{}")'.format(order_no),
            'fawvw_order')
        bm.do_mysql_exec('delete from `order` where ex_order_no="{}" and origin="BM"'.format(ex_order), 'fawvw_order')


@allure.suite('order')
@allure.title('BM适配层更新订单')
@pytest.mark.order
@pytest.mark.parametrize('d', [('INIT', 'jojo'), (None, None), ('PROCESSING', 'kaka')])
def test_update_bm_order(d):
    '''
    测试BM适配层更新订单接口
    '''
    order = bm.do_mysql_select(' SELECT * FROM `order` WHERE origin="BM" and vin is not null and del_flag=0', 'fawvw_order')
    order = random.choice(order)
    order_no = order['order_no']
    vin = order['vin']
    uid = order['aid']
    businessInfo = bm.f.pydict(4, True, value_types=str)
    businessState = d[0]
    businessStateDesc = d[1]
    event = bm.f.sentence()

    bm.update_bm_order(order_no, vin, uid, '1', businessExtInfo=businessInfo, businessState=businessState,
                       businessStateDesc=businessStateDesc, orderEvent=event)
    sql_res = bm.do_mysql_select('SELECT * FROM `order` WHERE order_no="{}"'.format(order_no), 'fawvw_order')
    if d[0] is not None and d[1] is not None:
        assert sql_res[0]['business_status'] == businessState
        assert sql_res[0]['business_status_desc'] == businessStateDesc
    order_id = sql_res[0]['id']
    sql_res_detail = bm.do_mysql_select('select detail from order_detail where order_id={}'.format(order_id), 'fawvw_order')
    assert len(sql_res_detail) == 1


@allure.suite('order')
@allure.title('BM车机端获取订单详情')
@pytest.mark.order
@pytest.mark.parametrize('d', [('221', '29515778243258532831'), ('33', '20201104165745583380928'),
                               ('4612472', '4612472112221')])
def test_bm_order_detail_aid(d):
    '''
    测试BM车机端获取订单详情，header传入aid
    :param d:
    :return:
    '''
    res = bm.bm_order_detail(d[0], d[1], bm.random_vin())
    assert res['data']['orderCategory']
    assert res['data']['orderStatus']


@allure.suite('order')
@allure.title('BM车机端获取订单详情')
@pytest.mark.order
def test_bm_order_detail_token():
    '''
    测试BM车机端获取订单详情，header传入aid
    :param d:
    :return:
    '''
    token = 'eyJraWQiOiJiYzEzZjMzNy05MjY3LTQyNTktYTQzZS02NmZkY2Q4MTc4NzQiLCJhbGciOiJSUzI1NiJ9.eyJpc3MiOiJodHRwczovL2lkcC11YXQubW9zYy5mYXctdncuY29tIiwiYW1yIjoicHdkIiwidHlwZSI6IkFUIiwiYXVkIjpbIlZXR01CQjAxQ05BUFAxIiwiYXV0b25hdmkuY29tIiwiWDlHLTEwMjE3LjA2LjE5OTk5OTAwMTIiXSwic3ViIjoiOTM1MTUyNCIsImlhdCI6MTYwNDkyMzUzOSwidmVyIjoiMC4wLjEiLCJ2aW4iOiJDMzE1MkQwMkZGMjlBRDgzRkI5MjJBQzE0QTRCOUM3QyIsImV4cCI6MTYwNTA5NjMzOSwianRpIjoiOTczZDI0NDAtNTRmNy00YjYyLTg1ZDgtMWEzYWU4MzNhMjM5IiwiY29yIjoiQ04iLCJhaWQiOiI5MzUxNTI0IiwidG50IjoiVldfSFVfQ05TM19YOUctMTAyMTcuMDYuMTk5OTk5MDAxMl92My4wLjFfdjAuMC4xIiwiaWR0LWlkIjoiNDEyYzQwOTktMGZkYy00MmNjLTljYjEtZWQxY2EyNWE0OTliIiwic2NwIjoiYWNjb3VudCIsInJ0LWlkIjoiY2I1ODhkMjMtMjY2NC00MWJjLTllZjUtZmIwOTM1NzIwMjc5In0.jc2jdPTpob0T1k-fUYTfDTjmZlkwdJo1QdPpyxgjKVyd6x1DiG6Pt3OZd7qngrx_2FJOoN2k8KGvdHIxhqe4EA'
    res = bm.bm_order_detail(None,order_no='111124424523',vin=bm.random_vin(),token=token)
    assert res['data']['orderCategory']
