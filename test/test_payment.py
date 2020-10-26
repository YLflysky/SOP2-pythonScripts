import pytest
import os
from order.payment import Payment
import random
import time
import json
import allure
import sys

os.environ['GATE'] = 'false'
os.environ['ENV'] = 'LOCAL'

pay = Payment()


@allure.suite('payment')
@allure.story('get result')
@pytest.mark.payment
@pytest.mark.parametrize('d',[('1234','1234'),('1235','1234'),('20200907105829249819204','32432')])
def test_get_pay_result(d):
    res = pay.get_pay_result(d[0],d[1])
    sql = pay.do_mysql_select('select * from pay_order where order_no="{}"'.format(d[0]),'mosc_pay')
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
