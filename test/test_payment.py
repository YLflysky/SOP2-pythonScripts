import pytest
import os
from order.payment import Payment
import random
import time
import json
import allure
import sys

os.environ['GATE'] = 'false'
os.environ['ENV'] = 'DEV'

pay = Payment()


@allure.suite('payment')
@allure.story('get result')
@pytest.mark.payment
@pytest.mark.parametrize('d',[('1234','1234'),('1235','1234'),('20200907105829249819204','32432')])
def test_get_pay_result(d):
    res = pay.get_pay_result(d[0],d[1])
    sql = pay.do_mysql_select('select * from pay_order where order_no="{}"'.format(d[0]),'mosc_pay')
    if sql[0]['buyer_account']:
        assert res['data']['buyerAccount'] == sql[0]['buyer_account']
    status = sql[0]['pay_status']
    if status == 'SUCCESS':
        assert res['data']['payResultStatus'] == '101'
    elif status == 'FAILED':
        assert res['data']['payResultStatus'] == '102'
    else:
        assert res['data']['payResultStatus'] == '100'


@allure.suite('payment')
@allure.story('get result')
@pytest.mark.payment
@pytest.mark.parametrize('d',[(pay.f.pyint(),'123','支付订单不存在'),
                              (None,'123',"Required String parameter 'orderNo' is not present"),
                              ('123',None,"Required String parameter 'aid' is not present")])
def test_get_pay_result_fail(d):
    '''
    输入的order_no不存在，无查询结果
    '''
    res = pay.get_pay_result(d[0],d[1])
    assert d[2] == res['errorMessage']


@allure.suite('payment')
@allure.story('get agreement')
@pytest.mark.payment
@pytest.mark.parametrize('d',[('在线','11112223','11101','en-US','ENGLISH'),('在线','111124424523','12101','zh-CN','荒野求生')])
def test_get_pay_agreement(d):
    '''
    测试获取支付协议
    '''
    res = pay.get_pay_agreement(uid=d[0],code=d[2],order_no=d[1],lang=d[3])
    assert res['data']['title'] == d[-1]


@allure.suite('payment')
@allure.story('get agreement')
@pytest.mark.payment
@pytest.mark.parametrize('d',[('221','33596893367386636663','11101','zh-CN','服务条款及免责声明（测试使用）'),
                              ('U002','20201012060626794180224','12101','en-US','Terms of Service and Disclaimer (Used for Testing)')])
def test_get_pay_agreement_default(d):
    '''
    测试默认获取支付协议
    '''
    res = pay.get_pay_agreement(uid=d[0],code=d[2],order_no=d[1],lang=d[3])
    assert res['data']['title'] == d[4]


@allure.suite('payment')
@allure.story('get agreement')
@pytest.mark.payment
@pytest.mark.parametrize('d',[(None,'11112223','11101','EN-US',"Required String parameter 'aid' is not present"),
                              ('在线',None,'12101','zh-CN',"Required String parameter 'orderNo' is not present"),
                         ('在线','abc','12101','zh-CN',"Feign调用order获取订单数据错误"),
                            ('在线','11112223',None,'zh-CN',"Required String parameter 'agreementCode' is not present"),
                              ('32432','20200907105829249819204','12101','Japanese','不支持的语言')])
def test_get_pay_agreement_fail(d):
    '''
    测试获取支付协议失败情况
    '''
    res = pay.get_pay_agreement(uid=d[0],code=d[2],order_no=d[1],lang=d[3])
    assert res['errorMessage'] ==d[-1]


callback_data = [('trade_success','2018091361389377','qwer',pay.f.pyfloat(2,2,True),pay.time_delta(),'123')]

@allure.suite('payment')
@allure.story('cdp callback')
@pytest.mark.payment
@pytest.mark.parametrize('d',callback_data)
def test_ali_pay_cdp_callback_01(d):
    '''
    测试获取支付宝cdp回调结果，输入全部必填项
    '''

    res = pay.ali_pay_callback(trade_status=d[0],app_id=d[1],out_trade_no=d[2],receipt_amount=d[3],gmt_payment=d[4],trade_no=d[5])
    assert res == 'success'
    pay_res = pay.do_mysql_select('select * from order_pay where pay_no="{}"'.format(d[5]),'order')
    assert pay_res[0]['pay_channel'] == 'ALI_PAY'
    assert pay_res[0]['pay_no'] == d[5]
    assert pay_res[0]['pay_way'] == 'QR_CODE'
    assert pay_res[0]['pay_amount'] ==d[3]
    assert pay_res[0]['pay_time'] == d[4]

@allure.suite('payment')
@allure.story('cdp callback')
@pytest.mark.payment
def test_ali_pay_cdp_callback_02():
    '''
    测试获取支付宝cdp回调结果，回调参数加上选填项
    '''
    status = 'trade_success'
    app_id = '2018091361389377'
    out_trade_no = 'ABCD'
    receipt_amount = 99.99
    gmt_payment= pay.time_delta(days=-1)
    trade_no = '10000'
    seller_email = pay.f.email()
    buyer_logon_id = pay.f.email()
    seller_id = pay.f.pyint(10000,10000000)
    buyer_id = pay.f.pyint(10000,10000000)
    total = 100.00
    res = pay.ali_pay_callback(status,app_id,out_trade_no,receipt_amount,gmt_payment,trade_no,
                               buyer_logon_id=buyer_logon_id,total_amount=total)
    assert res == 'success'
    pay_res = pay.do_mysql_select('select * from order_pay where pay_no="{}"'.format(trade_no),'order')
    assert pay_res[0]['pay_channel'] == 'ALI_PAY'
    assert pay_res[0]['pay_no'] == trade_no
    assert pay_res[0]['pay_way'] == 'QR_CODE'
    assert pay_res[0]['pay_amount'] == receipt_amount
    assert pay_res[0]['pay_time'] == gmt_payment
    order_no = pay.do_mysql_select('select order_no from order_id_relation where out_order_no="{}"'.format(out_trade_no),'mosc_pay')
    order_no = order_no[0]['order_no']
    order_res = pay.do_mysql_select('select * from `order` where order_no="{}"'.format(order_no),'order')
    aid = order_res[0]['aid']
    res = pay.get_pay_result(order_no,aid=aid)
    assert res['data']['buyerAccount'] == buyer_logon_id
    assert res['data']['payResultStatus'] == '101'


callback_data_fail = [('trade_fail','2018091361389377','qwer',pay.f.pyfloat(2,2,True),pay.time_delta(),'123'),
                      ('trade_success','20180913613893770','qwer',pay.f.pyfloat(2,2,True),pay.time_delta(),'123'),
                      ('trade_success','2018091361389377','out_trade_no',pay.f.pyfloat(2,2,True),pay.time_delta(),'123'),
                      ('trade_success','20180913613893770','qwer',pay.f.pyfloat(2,2,True),None,'123')]

@allure.suite('payment')
@allure.story('cdp callback')
@pytest.mark.payment
@pytest.mark.parametrize('d',callback_data_fail)
def test_ali_pay_cdp_callback_03(d):
    '''
    测试获取支付宝cdp回调结果，异常情况测试
    '''

    res = pay.ali_pay_callback(trade_status=d[0],app_id=d[1],out_trade_no=d[2],receipt_amount=d[3],gmt_payment=d[4],trade_no=d[5])
    assert res == 'fail'
