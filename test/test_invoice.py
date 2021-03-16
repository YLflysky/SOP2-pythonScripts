import time

from .conftest import order
import pytest
import allure
import sys
import random

success_data = [{'aid': '123456', 'invoiceNo': '1881413'},
                {'aid': '123456', 'invoiceNo': '282249'},
                {'aid': '4614907', 'invoiceNo': '38133119'},
                {'aid': '4614233', 'invoiceNo': 'Y22WPIE91582092H06X1615793065282'},
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
    sql = order.do_mysql_select('select * from order_invoice where invoice_no="{}"'.format(param['invoiceNo']), 'fawvw_order')
    print(sql)
    assert len(sql) == 1
    assert sql[0]['status'] == res['data']['status']
    assert sql[0]['invoice_no'] == res['data']['invoiceNo']
    assert sql[0]['transmission_time'] == res['data']['transmissionTime']


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
def test_sync_invoice_03():
    '''
    测试同步发票信息，传入已存在的发票更改信息
    '''
    invoice_no='907998'
    status='SUCCESS'
    party = random.choice(['PERSONAL','COMPANY'])
    order_no = ['ftb20210315140416705172032']
    order.sync_invoice(invoice_no,status,party,order_no)
    sql_res = order.do_mysql_select('select * from order_invoice where invoice_no={}'.format(invoice_no),'fawvw_order')
    assert sql_res[0]['status'] == status
    assert sql_res[0]['party_type'] == party
    sql_res = order.do_mysql_select('select * from `order` where order_no="ftb20210315140416705172032"','fawvw_order')
    assert sql_res[0]['invoice_status'] == '2'
    with allure.step('测试结果'):
        allure.attach(status,'发票状态',attachment_type=allure.attachment_type.TEXT)
        allure.attach(party,'发票抬头',attachment_type=allure.attachment_type.TEXT)