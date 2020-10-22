import pytest
import os
from order.oder_api import Order
import random
import time
import json
import allure
import sys

os.environ['ENV'] = 'UAT'
os.environ['GATE'] = 'false'
o = Order()

success_data = [{'aid': '123456', 'invoiceNo': '1881413'},
                {'aid': '123456', 'invoiceNo': '4738440'},
                {'aid': '4614907', 'invoiceNo': '38133119'},
                {'aid': '4614931', 'invoiceNo': '38133230'}]


@allure.suite('order')
@allure.story('invoiceDetail')
@pytest.mark.order
@pytest.mark.parametrize('param', success_data)
def test_invoice_detail_success(param):
    res = o.invoice_detail(param['aid'], param['invoiceNo'])
    assert 'SUCCEED' == res['returnStatus']
    SQL_RES = o.do_mysql_select('select * from order_invoice where invoice_no="{}"'.format(param['invoiceNo']), 'order')
    print(SQL_RES)
    assert len(SQL_RES) == 1
    assert SQL_RES[0]['status'] == res['data']['status']
    assert SQL_RES[0]['invoice_no'] == res['data']['invoiceNo']
    assert SQL_RES[0]['transmission_time'] == res['data']['transmissionTime']


fail_data = [{'aid': None, 'serialNo': 'serial_no_0001'},
             {'aid': '123', 'serialNo': None},
             {'aid': '123', 'serialNo': 'abcd123'},
             {'aid': '1234', 'serialNo': '3'}, {'aid': None, 'serialNo': None}]


@allure.suite('order')
@allure.story('invoiceDetail')
@pytest.mark.order
@pytest.mark.parametrize('param', fail_data)
def test_invoice_detail_fail(param):
    res = o.invoice_detail(param['aid'], param['serialNo'])
    assert 'FAILED' == res['returnStatus']


@allure.suite('order')
@allure.story('invoiceDetail')
@pytest.mark.order
def test_gas_invoice_detail():
    '''
    测试加油业务域发票详情
    '''
    param = o.do_mysql_select('select * from order_invoice where service_id="GAS" and id in'
                              ' (select invoice_id from order_invoice_relation)', 'order')
    if len(param) == 0:
        print('no test data...exit test')
        sys.exit(-1)
    param = random.choice(param)
    res = o.invoice_detail(param['aid'], param['invoice_no'])
    assert 'SUCCEED' == res['returnStatus']
    assert param['status'] == res['data']['status']
    assert param['invoice_no'] == res['data']['invoiceNo']
    assert param['transmission_time'] == res['data']['transmissionTime']
    assert param['tax'] == res['data']['tax']
    assert param['address_tel'] == res['data']['addressTel']


data = [
    {'epOrderId': '22233442', 'invoiceNo': random.randint(100, 1000), 'status': 'NOT_ISSUED', 'partyType': 'PERSONAL'},
    {'epOrderId': '22233442', 'invoiceNo': random.randint(100, 1000), 'status': 'PENDING', 'partyType': 'PERSONAL'},
    {'epOrderId': '22233442', 'invoiceNo': random.randint(100, 1000), 'status': 'SUCCESS', 'partyType': 'PERSONAL'},
    {'epOrderId': '22233442', 'invoiceNo': random.randint(100, 1000), 'status': 'FAILED', 'partyType': 'PERSONAL'},
    {'epOrderId': '22233442', 'invoiceNo': random.randint(100, 1000), 'status': 'SUCCESS', 'partyType': 'COMPANY'},
]


@allure.suite('order')
@allure.story('syncInvoice')
@pytest.mark.parametrize('d', data)
@pytest.mark.order
def test_sync_invoice(d):
    ex_order_no = d['epOrderId']
    invoice_no = d['invoiceNo']
    status = d['status']
    party_type = d['partyType']
    o.teardown_sync(ex_order_no, invoice_no)
    o.sync_invoice(ex_order_no, invoice_no, status, party_type)
    sql = o.do_mysql_select('select * from order_invoice where invoice_no="{}"'.format(invoice_no), 'order')
    assert len(sql) == 1
    body = o.invoice_detail(sql[0]['aid'], invoice_no)
    assert 'SUCCEED' == body['returnStatus']
    assert status == body['data']['status']
    assert party_type == body['data']['invoiceType']


@allure.suite('order')
@allure.story('orderNo')
@pytest.mark.order
def test_generate_orderNo():
    body = o.generate_order_no()
    assert 'SUCCEED' == body['returnStatus']
    assert body['data'] is not None


@allure.suite('order')
@allure.story('sync pay')
@pytest.mark.order
def test_sync_pay():
    '''
    测试同步支付结果
    '''
    sql = o.do_mysql_select('select aid,order_no from  `order` where del_flag=0', db='order')
    sql = random.choice(sql)
    aid = sql['aid']
    order_no = sql['order_no']
    pay_no = o.f.pyint()
    o.sync_order_pay(aid, order_no, pay_no, )
    res = o.do_mysql_select('select count(1) from order_pay where pay_no = {}'.format(pay_no), 'order')
    assert len(res) == 1
    o.do_mysql_exec('delete from order_pay where pay_no={}'.format(pay_no), 'order')


@allure.suite('order')
@allure.story('syncInvoice')
@pytest.mark.order
def test_apply_invoice():
    '''
    测试申请开发票接口
    '''
    aid = '4614907'
    order_no = o.do_mysql_select(
        'select order_no from `order` where aid={} and service_id="GAS" and '
        ' order_status="PAY_SUCCESS" and invoice_issuable=1 and invoice_status=0'.format(
            aid), 'order')
    if len(order_no) == 0:
        print('没有可以开票的测试数据，退出测试...')
        sys.exit(-1)

    order_no = random.choice(order_no)['order_no']
    order_no = ['20201013105955077200704']
    phone = '18888888888'
    head = '钛马信息技术有限公司'
    duty = '91310115560364240G'
    o.apply_invoice(aid, order_no, duty, head, phone)
    sql_res = o.do_mysql_select('select invoice_status from `order` where order_no={}'.format(order_no[0]), 'order')
    assert sql_res[0]['invoice_status'] == 1


@allure.suite('order')
@allure.story('callback')
@pytest.mark.order
def test_callback_order():
    ep_order = '123456789'
    info = {'name': 'waka waka', 'age': 18}
    o.do_mysql_exec('delete from `order` where ex_order_no="{}"'.format(ep_order), 'order')

    o.sync_order_kafka(ep_order, info, cp="NX_ENGINE")
    time.sleep(2.0)
    sql_res = o.do_mysql_select(
        'select d.detail,o.* '
        'from `order` o,order_detail d where o.id=d.order_id and ex_order_no="{}"'.format(
            ep_order), 'order')
    print('同步订单成功')
    assert len(sql_res) == 1
    assert sql_res[0]['order_status'] == 'PAY_SUCCESS'
    assert sql_res[0]['business_status'] == 'SUCCESS_PAY'
    assert sql_res[0]['business_status_desc'] == 'zdh测试'
    assert sql_res[0]['vin'] == 'DEFAULT_VIN'
    assert sql_res[0]['category'] == '105'
    assert sql_res[0]['sp_id'] == 'NX_ENGINE'
    assert sql_res[0]['service_id'] == 'GAS'
    assert str(sql_res[0]['total_amount']) == '6.0'
    assert sql_res[0]['ex_order_no'] == ep_order
    print('同步订单ex_order_no成功:{}'.format(ep_order))
    info = json.dumps(info, sort_keys=True)
    assert sql_res[0]['detail'] == info
    print("同步business info成功：{}".format(info))


@allure.suite('order')
@allure.story('callback')
@pytest.mark.order
def test_callback_invoice():
    '''
    测试发票的callback
    :return:
    '''
    ep_order = 1
    invoice_no = random.randint(1, 100)
    price = o.f.pyint(1.00, 100.00)
    print('初始化环境....')
    o.teardown_sync(ep_order, invoice_no)

    o.sync_invoice_kafka(ep_order, invoice_no, price)
    time.sleep(2.0)
    sql_res = o.do_mysql_select(
        'select i.*,r.invoice_id from order_invoice i,order_invoice_relation r where i.id=r.invoice_id and i.invoice_no="{}"'.format(
            invoice_no), 'order')

    assert len(sql_res) == 1
    assert sql_res[0]['sp_id'] == 'NX_ENGINE'
    assert sql_res[0]['price'] == price
    assert sql_res[0]['invoice_no'] == str(invoice_no)
    assert sql_res[0]['invoice_id'] == sql_res[0]['id']


@allure.suite('order')
@allure.story('sync')
@pytest.mark.order
@pytest.mark.parametrize('order_status', ['INIT', 'WAITING_PAY', 'PROCESSING', 'REFUND_FAILED', 'REFUND_SUCCESS',
                                          'PAY_SUCCESS', 'PAY_FAILED', 'CANCEL', 'FINISH', 'EXPIRE', 'REFUNDING',
                                          'RESERVED'])
def test_sync_order_01(order_status):
    '''
    同步订单接口测试，订单状态枚举
    '''
    ex = 'test001'
    origin = 'EP'
    aid = '123456'
    category = '102'
    res = o.sync_order(ex, origin, aid, category, orderStatus=order_status, timeout=20)
    sql_res = o.do_mysql_select('select order_status from `order` where order_no="{}"'.format(res['data']), 'order')
    assert len(sql_res) == 1
    assert sql_res[0]['order_status'] == order_status
    o.do_mysql_exec('delete from `order` where order_no="{}"'.format(res['data']), 'order')


@allure.suite('order')
@allure.story('sync')
@pytest.mark.order
@pytest.mark.parametrize('order_type', ['RESERVATION', 'COMMODITY', 'BUSINESS'])
def test_sync_order_02(order_type):
    '''
    同步订单接口测试，订单类型枚举
    '''
    ex = 'test001'
    origin = 'EP'
    aid = '123456'
    category = '102'
    res = o.sync_order(ex, origin, aid, category, orderType=order_type, checkFlag=True)
    sql_res = o.do_mysql_select('select * from `order` where order_no="{}"'.format(res['data']), 'order')
    assert len(sql_res) == 1
    o.do_mysql_exec('delete from `order` where order_no="{}"'.format(res['data']), 'order')


@allure.suite('order')
@allure.story('sync')
@pytest.mark.order
@pytest.mark.parametrize('origin', ['SELF', 'EP', 'BM', 'MA', 'VPA', 'OTHER'])
def test_sync_order_03(origin):
    '''
    同步订单接口测试，订单来源枚举
    '''
    ex = 'test001'
    aid = '123456'
    category = '102'
    res = o.sync_order(ex, origin, aid, category)
    sql_res = o.do_mysql_select('select origin from `order` where order_no="{}"'.format(res['data']), 'order')
    assert len(sql_res) == 1
    assert sql_res[0]['origin'] == origin
    o.do_mysql_exec('delete from `order` where order_no="{}"'.format(res['data']), 'order')


@allure.suite('order')
@allure.story('sync')
@pytest.mark.order
def test_sync_order_reservation():
    '''
    测试同步订单为预约单轮询检查订单状态功能

    '''
    ex = o.f.pyint()
    aid = '123456'
    category = '102'
    status = 'INIT'
    service = '111'

    res = o.sync_order(ex, 'VPA', aid, category, orderType='RESERVATION', checkFlag=True, orderStatus=status,
                       serviceId=service, spId=o.f.pyint())

    time.sleep(15.0)
    sql_res = o.do_mysql_select('select * from `order` where order_no="{}"'.format(res['data']), 'order')
    try:
        assert len(sql_res) == 1
        assert sql_res
        assert sql_res[0]['order_status'] == 'FINISH'
        assert sql_res[0]['check_flag'] == '0'
    finally:
        pass
        o.do_mysql_exec('delete from `order` where order_no="{}"'.format(res['data']), 'order')


@allure.suite('order')
@allure.story('update')
@pytest.mark.order
def test_update_order():
    '''
    测试更新订单，更新订单状态,业务信息
    '''
    ex = 'test001'
    aid = '123456'
    category = '102'
    origin = 'EP'
    res = o.sync_order(ex, origin, aid, category)
    order_no = res['data']
    business_info = {'name': 'sergio', 'age': '27', 'weight': '145', 'height': '174'}
    o.update_order(order_no=order_no, aid=aid, orderStatus='INIT', businessInfo=business_info)
    sql_res = o.do_mysql_select(
        'select order_status,detail from `order` o,order_detail d where 1=1 and o.id=d.order_id and order_no="{}"'.format(
            order_no), 'order')
    try:
        assert sql_res[0]['order_status'] == 'INIT'
        sql_res_detail = json.loads(sql_res[0]['detail'])
        assert sql_res_detail['age'] == business_info['age']
        assert sql_res_detail['name'] == business_info['name']
        assert sql_res_detail['weight'] == business_info['weight']
        assert sql_res_detail['height'] == business_info['height']
    finally:
        pass
        o.do_mysql_exec('delete from `order` where order_no="{}"'.format(order_no), 'order')
