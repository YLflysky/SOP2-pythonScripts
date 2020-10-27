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
                            ('在线','11112223',None,'zh-CN',"Required String parameter 'agreementCode' is not present")])
def test_get_pay_agreement_fail(d):
    '''
    测试获取支付协议失败情况
    '''
    res = pay.get_pay_agreement(uid=d[0],code=d[2],order_no=d[1],lang=d[3])
    assert res['errorMessage'] ==d[-1]
