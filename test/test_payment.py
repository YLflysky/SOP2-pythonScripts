import pytest
import os
from order.payment import Payment
import random
import time
import json
import allure
import sys

pay = Payment()


@allure.suite('payment')
@allure.story('get result')
@pytest.mark.payment
@pytest.mark.parametrize('d',[('1234','1234'),('1235','1234'),('20200907105829249819204','32432'),('orderNo0001','9642113')],
                         ids=['支付成功','支付失败','支付中','成功'])
def test_get_pay_result(d):
    res = pay.get_pay_result(d[0],d[1])
    sql = pay.do_mysql_select('select * from pay_order where order_no="{}" order by pay_time desc limit 1'.format(d[0]),'mosc_pay')
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
                              ('123',None,"Required String parameter 'aid' is not present")],
                         ids=['不存在订单','不传orderNo','不传aid'])
def test_get_pay_result_fail(d):
    '''
    测试查询支付结果，异常情况
    '''
    res = pay.get_pay_result(d[0],d[1])
    assert d[2] == res['errorMessage']


@allure.suite('payment')
@allure.story('get agreement')
@pytest.mark.payment
@pytest.mark.parametrize('d',[('9642113','11112223','11101','en-US','ENGLISH'),('9642113','111124424523','12101','zh-CN','荒野求生')]
                         ,ids=['支付宝英文协议','微信中文协议'])
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
                              ('U002','20201012060626794180224','12101','en-US','Terms of Service and Disclaimer (Used for Testing)')]
                         ,ids=['默认中文协议','默认英文协议'])
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
                              ('32432','20200907105829249819204','12101','Japanese','不支持的语言'),
                              ('32432','20200907105829249819204','agreementCode','zh-CN','无效的支付协议码')],
                         ids=['不传aid','不传orderNo','没有该订单','不传code','传入语言错误','传入code错误'])
def test_get_pay_agreement_wrong(d):
    '''
    测试获取支付协议，异常情况
    '''
    res = pay.get_pay_agreement(uid=d[0],code=d[2],order_no=d[1],lang=d[3])
    assert res['errorMessage'] ==d[-1]


callback_data = [('trade_success','2018091361389377','e6ef423f23194a4f8a924027c37917d1',pay.f.pyfloat(2,2,True),pay.time_delta(),pay.f.pyint()),
                 ('trade_success','2018091361389377','c94ed68006f847969c53db5506513152',pay.f.pyfloat(2,2,True),pay.time_delta(days=-10),pay.f.pyint())]

@allure.suite('payment')
@allure.story('cdp callback')
@pytest.mark.payment
@pytest.mark.parametrize('d',callback_data,ids=['order_no=M202007160901278277176514','order_no=orderNo0001'])
def test_ali_pay_cdp_callback_01(d):
    '''
    测试获取支付宝cdp回调结果，输入全部必填项
    '''

    res = pay.ali_pay_callback(trade_status=d[0],app_id=d[1],out_trade_no=d[2],receipt_amount=d[3],gmt_payment=d[4],trade_no=d[5])
    assert res == 'success'
    # 检查支付结果同步到订单中
    try:
        pay_res = pay.do_mysql_select('select * from order_pay where pay_no={}'.format(d[5]),'order')
        assert pay_res[0]['pay_channel'] == 'ALI_PAY'
        assert pay_res[0]['pay_no'] == str(d[5])
        assert pay_res[0]['pay_way'] == 'QR_CODE'
        assert pay_res[0]['pay_amount'] ==d[3]
        assert pay_res[0]['pay_time'] == d[4]
        assert pay_res[0]['pay_status'] == 'SUCCESS'
    finally:
        pay.do_mysql_exec('delete from order_pay where pay_no="{}"'.format(d[5]),'order')


@allure.suite('payment')
@allure.story('cdp callback')
@pytest.mark.payment
def test_ali_pay_cdp_callback_02():
    '''
    测试获取支付宝cdp回调结果，回调参数加上选填项
    '''
    status = 'trade_success'
    app_id = '2018091361389377'
    out_trade_no = '228de2285c6d4c70b71f7b63f7949d77'
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
    # 校验支付结果同步到订单支付结果中
    pay_res = pay.do_mysql_select('select * from order_pay where pay_no="{}"'.format(trade_no),'order')
    assert pay_res[0]['pay_channel'] == 'ALI_PAY'
    assert pay_res[0]['pay_no'] == trade_no
    assert pay_res[0]['pay_way'] == 'QR_CODE'
    assert pay_res[0]['pay_amount'] == receipt_amount
    assert pay_res[0]['pay_time'] == gmt_payment
    # 校验支付结果同步到支付的支付记录中
    order_no = pay.do_mysql_select('select order_no from order_id_relation where out_order_no="{}"'.format(out_trade_no),'mosc_pay')
    order_no = order_no[0]['order_no']
    order_res = pay.do_mysql_select('select * from `order` where order_no="{}"'.format(order_no),'order')
    aid = order_res[0]['aid']
    res = pay.get_pay_result(order_no,aid=aid)
    assert res['data']['buyerAccount'] == buyer_logon_id
    assert res['data']['payResultStatus'] == '101'


@allure.suite('payment')
@allure.story('cdp callback')
@pytest.mark.payment
def test_ali_pay_cdp_callback_sop1():
    '''
    输入的out_trade_no不在FTB2.2数据库中查询到，调用SOP1的service
    '''
    status = 'trade_success'
    app_id = '2018091361389377'
    out_trade_no = pay.f.pyint(10000,1000000)
    receipt_amount = 99.99
    gmt_payment= pay.time_delta(days=-1)
    trade_no = '10000'
    res = pay.ali_pay_callback(status,app_id,out_trade_no,receipt_amount,gmt_payment,trade_no,)
    assert res == 'success'


callback_data_fail = [('trade_fail','2018091361389377','qwer',pay.f.pyfloat(2,2,True),pay.time_delta(),'123'),
                      ('trade_success','20180913613893770','qwer',pay.f.pyfloat(2,2,True),pay.time_delta(),'123'),
                      ('trade_success','2018091361389377','out_trade_no',pay.f.pyfloat(2,2,True),pay.time_delta(),'123'),
                      ('trade_success','20180913613893770','qwer',pay.f.pyfloat(2,2,True),None,'123')]

@allure.suite('payment')
@allure.story('cdp callback')
@pytest.mark.payment
@pytest.mark.parametrize('d',callback_data_fail,ids=['trade_status错误','app_id错误','out_trade_no错误','没传支付时间'])
def test_ali_pay_cdp_callback_wrong(d):
    '''
    测试获取支付宝cdp回调结果，异常情况测试
    '''

    res = pay.ali_pay_callback(trade_status=d[0],app_id=d[1],out_trade_no=d[2],receipt_amount=d[3],gmt_payment=d[4],trade_no=d[5])
    assert res == 'fail'



@allure.suite('payment')
@allure.story('cmcc callback')
@pytest.mark.payment
def test_cmcc_callback_01():
    '''
    测试回调免密支付结果接口--支付宝签约
    '''
    aid = pay.f.pyint()

    pay.cmcc_callback(aid,'2100010000',1,1,1)
    try:
        sql = pay.do_mysql_select('select * from contract_sign where aid="{}" and pay_channel="ALI_PAY"'.format(aid),'mosc_pay')
        assert sql[0]['pause_status'] == 'OPEN'
        assert sql[0]['sign_status'] == 'OPEN'
    finally:
        pay.do_mysql_exec('delete from contract_sign where aid="{}" and pay_channel="ALI_PAY"'.format(aid),'mosc_pay')

@allure.feature('payment')
@allure.suite('cmcc callback')
@pytest.mark.payment
def test_cmcc_callback_02():
    '''
    测试回调免密支付结果接口--支付宝解约
    '''
    aid = pay.f.pyint()

    pay.cmcc_callback(aid, '2100010000', 1, 2, 2)
    try:
        sql = pay.do_mysql_select('select * from contract_sign where aid="{}" and pay_channel="ALI_PAY"'.format(aid),
                                  'mosc_pay')
        assert sql[0]['pause_status'] == 'PAUSE'
        assert sql[0]['sign_status'] == 'CLOSE'
    finally:
        pay.do_mysql_exec('delete from contract_sign where aid="{}" and pay_channel="ALI_PAY"'.format(aid),
                          'mosc_pay')

@allure.suite('payment')
@allure.story('cmcc callback')
@pytest.mark.payment
def test_cmcc_callback_03():
    '''
    测试回调免密支付结果接口--微信签约
    '''
    aid = pay.f.pyint()

    pay.cmcc_callback(aid, '2100010000', 2, 1, 1)
    try:
        sql = pay.do_mysql_select('select * from contract_sign where aid="{}" and pay_channel="WECHAT_PAY"'.format(aid),
                                  'mosc_pay')
        assert sql[0]['pause_status'] == 'OPEN'
        assert sql[0]['sign_status'] == 'OPEN'
    finally:
        pay.do_mysql_exec('delete from contract_sign where aid="{}" and pay_channel="WECHAT_PAY"'.format(aid),
                          'mosc_pay')


@allure.suite('payment')
@allure.story('cmcc callback')
@pytest.mark.payment
def test_cmcc_callback_04():
    '''
    测试回调免密支付结果接口--微信解约
    '''
    aid = pay.f.pyint()

    pay.cmcc_callback(aid, '2100010000', 2, 2, 2)
    try:
        sql = pay.do_mysql_select('select * from contract_sign where aid="{}" and pay_channel="WECHAT_PAY"'.format(aid),
                                  'mosc_pay')
        assert sql[0]['pause_status'] == 'PAUSE'
        assert sql[0]['sign_status'] == 'CLOSE'
    finally:
        pay.do_mysql_exec('delete from contract_sign where aid="{}" and pay_channel="WECHAT_PAY"'.format(aid),
                          'mosc_pay')

@allure.suite('payment')
@allure.story('cmcc callback')
@pytest.mark.payment
@pytest.mark.parametrize('wrong',[('221','2100010000',2,1,2),('221','21000100001',2,1,1),
                                  ('221','2100010000',3,1,1),(None,'2100010000',1,1,1)],
                         ids=['输入类型和状态不一致','输入enterprise错误','输入channel错误','不输入aid'])
def test_cmcc_callback_wrong(wrong):
    '''
    测试回调免密支付结果接口--异常情况
    '''
    res = pay.cmcc_callback(aid=wrong[0],enterprise=wrong[1],channel=wrong[2],notify_type=wrong[3],status=wrong[4])
    assert res['errorMessage']