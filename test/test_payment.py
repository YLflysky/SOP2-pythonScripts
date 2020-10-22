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
@pytest.mark.parametrize('d',[('M202007160901278277176514','9349643'),('20200907105829249819205','32432')])
def test_get_pay_result(d):
    res = pay.get_pay_result(d[0],d[1])
    sql = pay.do_mysql_select('select buyer_account from pay_order where order_no="{}"'.format(d[0]),'mosc_pay')
    assert res['data']['buyerAccount'] == sql[0]['buyer_account']


@allure.suite('payment')
@allure.story('get result')
@pytest.mark.payment
@pytest.mark.parametrize('d',[(pay.f.pyint(),'123'),(None,'123'),('123',None)])
def test_get_pay_result_fail(d):
    '''
    输入的order_no不存在，无查询结果
    '''
    res = pay.get_pay_result(d[0],d[1])
    assert 'errorMessage' in res.keys()
