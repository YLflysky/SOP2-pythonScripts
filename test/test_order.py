import pytest
import os
from order.oder_api import Order
import random
import time
import json

os.environ['ENV'] = 'DEV'
os.environ['GATE'] = 'false'
o = Order()

success_data = [{'aid': 'admin', 'serialNo': '3'},
                {'aid': '123', 'serialNo': 'qwer'},
                {'aid': '123', 'serialNo': 'abcd'},
                {'aid': '123', 'serialNo': '1024'}]


@pytest.mark.order
@pytest.mark.parametrize('param', success_data)
def test_invoice_detail_success(param):
    res = o.invoice_detail(param['aid'], param['serialNo'])
    assert 'SUCCEED' == res['returnStatus']
    SQL_RES = o.do_mysql_select('select * from order_invoice where serial_no="{}"'.format(param['serialNo']), 'order')
    print(SQL_RES)
    assert len(SQL_RES) == 1
    assert SQL_RES[0]['status'] == res['data']['status']
    assert param['serialNo'] == res['data']['serialNo']
    assert SQL_RES[0]['transmission_time'] == res['data']['transmissionTime']


fail_data = [{'aid': None, 'serialNo': 'serial_no_0001'},
             {'aid': '123', 'serialNo': None},
             {'aid': '123', 'serialNo': 'abcd123'},
             {'aid': '1234', 'serialNo': '3'}, {'aid': None, 'serialNo': None}]


@pytest.mark.order
@pytest.mark.parametrize('param', fail_data)
def test_invoice_detail_fail(param):
    res = o.invoice_detail(param['aid'], param['serialNo'])
    assert 'FAILED' == res['returnStatus']


data = [
    {'epOrderId':'22233442','invoiceNo':random.randint(100,1000),'status':'NOT_ISSUED','partyType':'PERSONAL'},
    {'epOrderId':'22233442','invoiceNo':random.randint(100,1000),'status':'PENDING','partyType':'PERSONAL'},
    {'epOrderId':'22233442','invoiceNo':random.randint(100,1000),'status':'SUCCESS','partyType':'PERSONAL'},
    {'epOrderId':'22233442','invoiceNo':random.randint(100,1000),'status':'FAILED','partyType':'PERSONAL'},
    {'epOrderId':'22233442','invoiceNo':random.randint(100,1000),'status':'SUCCESS','partyType':'COMPANY'},
]


@pytest.mark.parametrize('d', data)
@pytest.mark.order
@pytest.mark.invoice
def test_sync_invoice(d):
    ex_order_no = d['epOrderId']
    invoice_no = d['invoiceNo']
    status = d['status']
    party_type = d['partyType']
    o.teardown_sync(ex_order_no, invoice_no)
    o.sync_invoice(ex_order_no,invoice_no,status,party_type)
    sql = o.do_mysql_select('select * from order_invoice where invoice_no="{}"'.format(invoice_no),'order')
    assert len(sql)==1
    body = o.invoice_detail(sql[0]['aid'],invoice_no)
    assert 'SUCCEED'==body['returnStatus']
    assert status==body['data']['status']
    assert party_type==body['data']['invoiceType']




@pytest.mark.NO
def test_generate_orderNo():
    body = o.generate_order_no()
    assert 'SUCCEED' == body['returnStatus']
    assert body['data'] is not None

@pytest.mark.callback
@pytest.mark.order
def test_callback_order():
    ep_order = '123456789'
    info = {'name': 'waka waka', 'age': 18}
    o.do_mysql_exec('delete from `order` where ex_order_no="{}"'.format(ep_order),'order')

    o.sync_order_kafka(ep_order, info,cp="NX_ENGINE")
    time.sleep(2.0)
    sql_res = o.do_mysql_select(
        'select d.detail,o.* '
        'from `order` o,order_detail d where o.id=d.order_id and ex_order_no="{}"'.format(
            ep_order), 'order')
    print('同步订单成功')
    assert len(sql_res) == 1
    assert sql_res[0]['order_status'] == 'FINISH'
    assert sql_res[0]['business_status'] == 'SUCCESS_PAY'
    assert sql_res[0]['business_status_desc'] == 'zdh测试'
    assert sql_res[0]['vin'] == 'DEFAULT_VIN'
    assert sql_res[0]['category'] == '105'
    assert sql_res[0]['sp_id'] == 'NX_ENGINE'
    assert sql_res[0]['service_id'] == 'GAS'
    assert sql_res[0]['price'] == '6.00'
    assert sql_res[0]['ex_order_no'] == ep_order
    print('同步订单ex_order_no成功:{}'.format(ep_order))
    info = json.dumps(info,sort_keys=True)
    assert sql_res[0]['detail'] == info
    print("同步business info成功：{}".format(info))

@pytest.mark.callback
@pytest.mark.order
def test_callback_invoice():
    '''
    测试发票的callback
    :return:
    '''
    ep_order = 1
    invoice_no = random.randint(1,100)
    price = o.f.pyint(1.00,100.00)
    print('初始化环境....')
    o.teardown_sync(ep_order,invoice_no)

    o.sync_invoice_kafka(ep_order,invoice_no,price)
    time.sleep(2.0)
    sql_res = o.do_mysql_select(
        'select i.sp_id,i.price,i.invoice_no '
        'from order_invoice i,order_invoice_relation r where i.id=r.invoice_id and i.invoice_no="{}"'.format(
            invoice_no), 'order')
    assert len(sql_res) == 1
    assert sql_res[0]['sp_id'] == 'NX_ENGINE'
    assert sql_res[0]['price'] == price
    assert sql_res[0]['invoice_no'] == str(invoice_no)


