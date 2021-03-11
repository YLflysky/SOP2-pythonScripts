import time

from .conftest import order
import pytest
import allure
import sys
import random

success_data = [{'aid': '123456', 'invoiceNo': '1881413'},
                {'aid': '123456', 'invoiceNo': '282249'},
                {'aid': '4614907', 'invoiceNo': '38133119'},
                {'aid': '4614931', 'invoiceNo': '38133230'}]


@allure.suite('order')
@allure.title('测试获取发票详情成功情况')
@pytest.mark.order
@pytest.mark.parametrize('param', success_data)
def test_invoice_detail_success(param):
    '''
    测试获取发票详情成功情况
    '''
    res = order.invoice_detail(param['aid'], param['invoiceNo'])
    assert 'SUCCEED' == res['returnStatus']
    SQL_RES = order.do_mysql_select('select * from order_invoice where invoice_no="{}"'.format(param['invoiceNo']), 'fawvw_order')
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
@allure.title('测试获取发票详情>>异常情况')
@pytest.mark.order
@pytest.mark.parametrize('param', fail_data)
def test_invoice_detail_fail(param):
    '''
    测试获取发票详情失败情况
    '''
    res = order.invoice_detail(param['aid'], param['serialNo'])
    assert 'FAILED' == res['returnStatus']


@allure.suite('order')
@allure.title('测试加油业务域发票详情')
@pytest.mark.order
def test_gas_invoice_detail():
    '''
    测试加油业务域发票详情
    '''
    param = order.do_mysql_select('select * from order_invoice where service_id="GAS" and id in'
                              '(select invoice_id from order_invoice_relation)', 'fawvw_order')
    if len(param) == 0:
        print('no test data...exit test')
        sys.exit(-1)
    param = random.choice(param)
    res = order.invoice_detail(param['aid'], param['invoice_no'])
    assert 'SUCCEED' == res['returnStatus']
    assert param['status'] == res['data']['status']
    assert param['invoice_no'] == res['data']['invoiceNo']
    assert param['transmission_time'] == res['data']['transmissionTime']
    assert param['tax'] == res['data']['tax']
    assert param['address_tel'] == res['data']['addressTel']


@allure.suite('order')
@allure.title('获取用户开票抬头')
@pytest.mark.order
def test_invoice_header():
    aid = '232'
    order.invoice_header(aid=aid)


@allure.suite('order')
@allure.title('申请开票>>流量订单')
@pytest.mark.order
def test_apply_invoice():
    '''
    测试申请开发票接口
    '''
    order_no = 'ftb20210310165155168876544'
    order_no = [order_no]
    aid = '9326335'
    phone = '18888888888'
    head = '钛马信息技术有限公司'
    duty = '91310115560364240G'
    order.apply_invoice(aid, order_no, duty, head, phone)
    try:
        sql_res = order.do_mysql_select('select invoice_status from `order` where order_no="{}"'.format(order_no), 'fawvw_order')

        assert sql_res[0]['invoice_status'] == 1
        sql_res = order.do_mysql_select('select * from order_invoice where order_no="{}"'.format(order_no),'fawvw_order')

        assert len(sql_res) == 1
    finally:
        pass

@allure.suite('order')
@allure.title('同步发票信息>>申请开票>>EP同步发票信息')
@pytest.mark.order
def test_sync_invoice():
    '''
    同步发票信息，一个发票信息仅含有一个订单
    '''

    order.apply_invoice()
    order.sync_invoice(invoice_no, status, party_type, ex_order_no,order_no)
    sql = order.do_mysql_select('select * from order_invoice where invoice_no="{}"'.format(invoice_no), 'fawvw_order')
    assert len(sql) == 1
    body = order.invoice_detail(sql[0]['aid'], invoice_no)
    assert 'SUCCEED' == body['returnStatus']
    assert status == body['data']['status']
    assert party_type == body['data']['invoiceType']



@allure.suite('order')
@allure.title('callback同步发票信息')
@pytest.mark.order
def test_callback_invoice():
    '''
    测试发票的callback
    :return:
    '''
    ep_order = ['1','222334442','22233442']
    invoice_no = 999
    price = order.f.pyfloat(right_digits=2,positive=True,min_value=1,max_value=10000)
    print('初始化环境....')
    order.teardown_sync_invoice(ep_order, invoice_no)
    aid = order.f.pyint()
    order.sync_invoice_kafka(ep_orders=ep_order, invoice=invoice_no, price=price,aid=aid)
    time.sleep(2.0)
    res = order.invoice_detail(str(aid),invoice_no)
    assert res['data']['userId'] == str(aid)
    assert float(res['data']['price']) == price
    assert res['data']['invoiceNo'] == str(invoice_no)
    assert len(res['data']['orderIdList']) == 3


@allure.suite('order')
@allure.title('同步发票信息')
@pytest.mark.order
def test_sync_invoice_02():
    '''
    测试多个订单开一个发票
    '''
    ex_order_no = ['2364','3322233']
    invoice_no = 10086
    status = 'SUCCESS'
    party_type = 'COMPANY'
    order.teardown_sync_invoice(ex_order_no, invoice_no)
    order.sync_invoice(invoice_no, status, party_type, ex_order_no)
    sql = order.do_mysql_select('select * from order_invoice where invoice_no="{}"'.format(invoice_no), 'fawvw_order')
    assert len(sql) == 1
    body = order.invoice_detail(sql[0]['aid'], invoice_no)
    assert 'SUCCEED' == body['returnStatus']
    assert status == body['data']['status']
    assert party_type == body['data']['invoiceType']
    assert len(body['data']['orderIdList']) == 2


@allure.suite('order')
@allure.title('同步发票信息')
@pytest.mark.order
def test_sync_invoice_03():
    '''
    测试同步发票信息，传入已存在的发票更改信息
    '''
    invoice_no='7200097'
    status=random.choice(['SUCCESS','PENDING','FAILED','NOT_ISSUED'])
    party = random.choice(['PERSONAL','COMPANY'])
    ep_order_id = ['3322333']
    order.sync_invoice(invoice_no,status,party,ep_order_id)
    sql_res = order.do_mysql_select('select * from order_invoice where invoice_no={}'.format(invoice_no),'fawvw_order')
    assert sql_res[0]['status'] == status
    assert sql_res[0]['party_type'] == party
    with allure.step('测试结果'):
        allure.attach(status,'发票状态',attachment_type=allure.attachment_type.TEXT)
        allure.attach(party,'发票抬头',attachment_type=allure.attachment_type.TEXT)