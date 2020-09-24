import pytest
import os
from base.base import Base
from order.oder_api import Order
import random

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


