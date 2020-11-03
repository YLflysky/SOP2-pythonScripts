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
@pytest.mark.parametrize('d', [('1234', '1234'), ('1235', '1234'), ('20200907105829249819204', '32432'),
                               ('orderNo0001', '9642113')],
                         ids=['支付成功', '支付失败', '支付中', '成功'])
def test_get_pay_result(d):
    res = pay.get_pay_result(d[0], d[1])
    sql = pay.do_mysql_select('select * from pay_order where order_no="{}" order by pay_time desc limit 1'.format(d[0]),
                              'mosc_pay')
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
@pytest.mark.parametrize('d', [(pay.f.pyint(), '123', '支付订单不存在'),
                               (None, '123', "Required String parameter 'orderNo' is not present"),
                               ('123', None, "Required String parameter 'aid' is not present")],
                         ids=['不存在订单', '不传orderNo', '不传aid'])
def test_get_pay_result_fail(d):
    '''
    测试查询支付结果，异常情况
    '''
    res = pay.get_pay_result(d[0], d[1])
    assert d[2] == res['errorMessage']


@allure.suite('payment')
@allure.story('get agreement')
@pytest.mark.payment
@pytest.mark.parametrize('d', [('9642113', '11112223', '11101', 'en-US', 'ENGLISH'),
                               ('9642113', '111124424523', '12101', 'zh-CN', '荒野求生')]
    , ids=['支付宝英文协议', '微信中文协议'])
def test_get_pay_agreement(d):
    '''
    测试获取支付协议
    '''
    res = pay.get_pay_agreement(uid=d[0], code=d[2], order_no=d[1], lang=d[3])
    assert res['data']['title'] == d[-1]


@allure.suite('payment')
@allure.story('get agreement')
@pytest.mark.payment
@pytest.mark.parametrize('d', [('221', '33596893367386636663', '11101', 'zh-CN', '服务条款及免责声明（测试使用）'),
                               ('U002', '20201012060626794180224', '12101', 'en-US',
                                'Terms of Service and Disclaimer (Used for Testing)')]
    , ids=['默认中文协议', '默认英文协议'])
def test_get_pay_agreement_default(d):
    '''
    测试默认获取支付协议
    '''
    res = pay.get_pay_agreement(uid=d[0], code=d[2], order_no=d[1], lang=d[3])
    assert res['data']['title'] == d[4]


@allure.suite('payment')
@allure.story('get agreement')
@pytest.mark.payment
@pytest.mark.parametrize('d', [(None, '11112223', '11101', 'EN-US', "Required String parameter 'aid' is not present"),
                               ('在线', None, '12101', 'zh-CN', "Required String parameter 'orderNo' is not present"),
                               ('在线', 'abc', '12101', 'zh-CN', "Feign调用order获取订单数据错误"),
                               ('在线', '11112223', None, 'zh-CN',
                                "Required String parameter 'agreementCode' is not present"),
                               ('32432', '20200907105829249819204', '12101', 'Japanese', '不支持的语言'),
                               ('32432', '20200907105829249819204', 'agreementCode', 'zh-CN', '无效的支付协议码')],
                         ids=['不传aid', '不传orderNo', '没有该订单', '不传code', '传入语言错误', '传入code错误'])
def test_get_pay_agreement_wrong(d):
    '''
    测试获取支付协议，异常情况
    '''
    res = pay.get_pay_agreement(uid=d[0], code=d[2], order_no=d[1], lang=d[3])
    assert res['errorMessage'] == d[-1]


callback_data = [('trade_success', '2018091361389377', 'e6ef423f23194a4f8a924027c37917d1', pay.f.pyfloat(2, 2, True),
                  pay.time_delta(), pay.f.pyint()),
                 ('trade_success', '2018091361389377', 'c94ed68006f847969c53db5506513152', pay.f.pyfloat(2, 2, True),
                  pay.time_delta(days=-10), pay.f.pyint())]


@allure.suite('payment')
@allure.story('cdp callback')
@pytest.mark.payment
@pytest.mark.parametrize('d', callback_data, ids=['order_no=M202007160901278277176514', 'order_no=orderNo0001'])
def test_ali_pay_cdp_callback_01(d):
    '''
    测试获取支付宝cdp回调结果，输入全部必填项
    '''

    res = pay.ali_pay_callback(trade_status=d[0], app_id=d[1], out_trade_no=d[2], receipt_amount=d[3], gmt_payment=d[4],
                               trade_no=d[5])
    assert res == 'success'
    # 检查支付结果同步到订单中
    try:
        pay_res = pay.do_mysql_select('select * from order_pay where pay_no={}'.format(d[5]), 'order')
        assert pay_res[0]['pay_channel'] == 'ALI_PAY'
        assert pay_res[0]['pay_no'] == str(d[5])
        assert pay_res[0]['pay_way'] == 'QR_CODE'
        assert pay_res[0]['pay_amount'] == d[3]
        assert pay_res[0]['pay_time'] == d[4]
        assert pay_res[0]['pay_status'] == 'SUCCESS'
    finally:
        pay.do_mysql_exec('delete from order_pay where pay_no="{}"'.format(d[5]), 'order')


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
    gmt_payment = pay.time_delta(days=-1)
    trade_no = '10000'
    seller_email = pay.f.email()
    buyer_logon_id = pay.f.email()
    seller_id = pay.f.pyint(10000, 10000000)
    buyer_id = pay.f.pyint(10000, 10000000)
    total = 100.00
    res = pay.ali_pay_callback(status, app_id, out_trade_no, receipt_amount, gmt_payment, trade_no,
                               buyer_logon_id=buyer_logon_id, total_amount=total)
    assert res == 'success'
    # 校验支付结果同步到订单支付结果中
    pay_res = pay.do_mysql_select('select * from order_pay where pay_no="{}"'.format(trade_no), 'order')
    assert pay_res[0]['pay_channel'] == 'ALI_PAY'
    assert pay_res[0]['pay_no'] == trade_no
    assert pay_res[0]['pay_way'] == 'QR_CODE'
    assert pay_res[0]['pay_amount'] == receipt_amount
    assert pay_res[0]['pay_time'] == gmt_payment
    # 校验支付结果同步到支付的支付记录中
    order_no = pay.do_mysql_select(
        'select order_no from order_id_relation where out_order_no="{}"'.format(out_trade_no), 'mosc_pay')
    order_no = order_no[0]['order_no']
    order_res = pay.do_mysql_select('select * from `order` where order_no="{}"'.format(order_no), 'order')
    aid = order_res[0]['aid']
    res = pay.get_pay_result(order_no, aid=aid)
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
    out_trade_no = pay.f.pyint(10000, 1000000)
    receipt_amount = 99.99
    gmt_payment = pay.time_delta(days=-1)
    trade_no = '10000'
    res = pay.ali_pay_callback(status, app_id, out_trade_no, receipt_amount, gmt_payment, trade_no, )
    assert res == 'success'


callback_data_fail = [('trade_fail', '2018091361389377', 'qwer', pay.f.pyfloat(2, 2, True), pay.time_delta(), '123'),
                      (
                          'trade_success', '20180913613893770', 'qwer', pay.f.pyfloat(2, 2, True), pay.time_delta(),
                          '123'),
                      ('trade_success', '2018091361389377', 'out_trade_no', pay.f.pyfloat(2, 2, True), pay.time_delta(),
                       '123'),
                      ('trade_success', '20180913613893770', 'qwer', pay.f.pyfloat(2, 2, True), None, '123')]


@allure.suite('payment')
@allure.story('cdp callback')
@pytest.mark.payment
@pytest.mark.parametrize('d', callback_data_fail, ids=['trade_status错误', 'app_id错误', 'out_trade_no错误', '没传支付时间'])
def test_ali_pay_cdp_callback_wrong(d):
    '''
    测试获取支付宝cdp回调结果，异常情况测试
    '''

    res = pay.ali_pay_callback(trade_status=d[0], app_id=d[1], out_trade_no=d[2], receipt_amount=d[3], gmt_payment=d[4],
                               trade_no=d[5])
    assert res == 'fail'


@allure.suite('payment')
@allure.story('cmcc callback')
@pytest.mark.payment
def test_cmcc_callback_01():
    '''
    测试回调免密支付结果接口--支付宝签约
    '''
    aid = pay.f.pyint()

    pay.cmcc_callback(aid, '2100010000', 1, 1, 1)
    try:
        sql = pay.do_mysql_select('select * from contract_sign where aid="{}" and pay_channel="ALI_PAY"'.format(aid),
                                  'mosc_pay')
        assert sql[0]['pause_status'] == 'OPEN'
        assert sql[0]['sign_status'] == 'OPEN'
    finally:
        pay.do_mysql_exec('delete from contract_sign where aid="{}" and pay_channel="ALI_PAY"'.format(aid), 'mosc_pay')


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
@pytest.mark.parametrize('wrong', [('221', '2100010000', 2, 1, 2), ('221', '21000100001', 2, 1, 1),
                                   ('221', '2100010000', 3, 1, 1), (None, '2100010000', 1, 1, 1)],
                         ids=['输入类型和状态不一致', '输入enterprise错误', '输入channel错误', '不输入aid'])
def test_cmcc_callback_wrong(wrong):
    '''
    测试回调免密支付结果接口--异常情况
    '''
    res = pay.cmcc_callback(aid=wrong[0], enterprise=wrong[1], channel=wrong[2], notify_type=wrong[3], status=wrong[4])
    assert res['errorMessage']


@allure.feature('payment')
@allure.story('sync pay stream')
@pytest.mark.payment
@pytest.mark.parametrize('enum', [('ALI_PAY', 'PROCESSING', 'QR_PAY', 'BM'), ('WECHAT_PAY', 'SUCCESS', 'APP', 'MA'),
                                  ('WECHAT_PAY', 'FAILED', 'FREE_PASS_PAY', 'SOP1'),
                                  ('UN_KNOWN', 'FAILED', 'FREE_PASS_PAY', 'FTB')]
    , ids=['支付宝-支付中-二维码-BM', '微信-支付成功-APP-MA', '微信-支付失败-免密-SOP1', '未知渠道-支付失败-免密-FTB'])
def test_sync_pay_stream(enum):
    '''
    测试同步支付记录，各个枚举值测试
    '''
    vin = pay.random_vin()
    aid = pay.f.pyint()
    ex_order = pay.f.md5()
    ex_pay_no = pay.f.sha1()
    order_no = pay.f.credit_card_number()
    pay_amount = 0.01
    order_amount = 1.00
    discount = 0.99
    channel = enum[0]
    pay_time = pay.time_delta()
    status = enum[1]
    origin = enum[3]
    pay_way = enum[2]
    service_id = 'MUSIC'
    sp_id = 'CLOUD_MUSIC'
    data = {'vin': vin, 'aid': aid, 'exOrderNo': ex_order, 'exPayNo': ex_pay_no, 'orderNo': order_no,
            'payAmount': pay_amount, 'orderAmount': order_amount, 'discountAmount': discount, 'payChannel': channel,
            'payStatus': status, 'payTime': pay_time, 'payWay': pay_way, 'serviceId': service_id, 'spId': sp_id,
            'origin': origin}
    pay.sync_pay_stream(data)
    try:
        sql_res = pay.do_mysql_select('select * from pay_order where ex_pay_no="{}"'.format(ex_pay_no), 'mosc_pay')
        assert len(sql_res) == 1
        sql_res = sql_res[0]
        assert sql_res['vin'] == vin
        assert sql_res['pay_time'] == pay_time
        assert sql_res['pay_amount'] == pay_amount
        assert sql_res['order_amount'] == order_amount
        assert sql_res['discount_amount'] == discount
        assert sql_res['order_no'] == order_no
        assert sql_res['ex_order_no'] == ex_order
        assert sql_res['pay_channel'] == channel
        assert sql_res['pay_way'] == pay_way
        assert sql_res['pay_status'] == status
        assert sql_res['order_source'] == origin
    finally:
        pay.do_mysql_exec('delete from pay_order where ex_pay_no="{}"'.format(ex_pay_no), 'mosc_pay')


@allure.feature('payment')
@allure.story('sync pay stream')
@pytest.mark.payment
def test_sync_pay_stream_xuantian():
    '''
    测试同步支付记录，选填参数测试
    '''
    vin = pay.random_vin()
    aid = pay.f.pyint()
    ex_order = pay.f.md5()
    ex_pay_no = pay.f.sha1()
    order_no = pay.f.credit_card_number()
    pay_amount = 0.01
    order_amount = 1.00
    discount = 0.99
    channel = 'ALI_PAY'
    pay_time = pay.time_delta()
    status = 'FAILED'
    origin = 'SOP1'
    pay_way = 'APP'
    service_id = 'MUSIC'
    sp_id = 'CLOUD_MUSIC'
    buyer = pay.f.email()
    reason = pay.f.sentence()
    data = {'vin': vin, 'aid': aid, 'exOrderNo': ex_order, 'exPayNo': ex_pay_no, 'orderNo': order_no,
            'payAmount': pay_amount, 'orderAmount': order_amount, 'discountAmount': discount, 'payChannel': channel,
            'payStatus': status, 'payTime': pay_time, 'payWay': pay_way, 'serviceId': service_id, 'spId': sp_id,
            'origin': origin,
            'buyerAccount': buyer, 'failReason': reason}
    pay.sync_pay_stream(data)
    try:
        sql_res = pay.do_mysql_select('select * from pay_order where ex_pay_no="{}"'.format(ex_pay_no), 'mosc_pay')
        assert len(sql_res) == 1
        sql_res = sql_res[0]
        assert sql_res['buyer_account'] == buyer
        assert sql_res['fail_reason'] == reason
    finally:
        pass


@allure.feature('payment')
@allure.story('sync pay stream')
@pytest.mark.payment
def test_sync_pay_stream_update():
    '''
    测试同步支付记录，传入的支付记录已存在，修改该条记录
    '''
    vin = pay.random_vin()
    aid = '7379'
    ex_order = 'f21816b94454352ce51f92b9db20d0b8'
    ex_pay_no = '0ba06b76a69957d6c9246fae53329f8271d1c522'
    order_no = '3554425509325059'
    pay_amount = 10052
    order_amount = 14589
    discount = 4396
    channel = 'ALI_PAY'
    pay_time = pay.time_delta()
    status = 'FAILED'
    origin = 'SOP1'
    pay_way = 'APP'
    service_id = 'MUSIC'
    sp_id = 'CLOUD_MUSIC'
    buyer = pay.f.email()
    reason = pay.f.sentence()
    data = {'vin': vin, 'aid': aid, 'exOrderNo': ex_order, 'exPayNo': ex_pay_no, 'orderNo': order_no,
            'payAmount': pay_amount, 'orderAmount': order_amount, 'discountAmount': discount, 'payChannel': channel,
            'payStatus': status, 'payTime': pay_time, 'payWay': pay_way, 'serviceId': service_id, 'spId': sp_id,
            'origin': origin,
            'buyerAccount': buyer, 'failReason': reason}
    pay.sync_pay_stream(data)
    try:
        sql_res = pay.do_mysql_select('select * from pay_order where ex_pay_no="{}"'.format(ex_pay_no), 'mosc_pay')
        assert len(sql_res) == 1
        sql_res = sql_res[0]
        assert sql_res['buyer_account'] == buyer
        assert sql_res['fail_reason'] == reason
    finally:
        pass


error = [(None, 'aid001', 'ex_order001', 'pay001', 'order001', 9999, 10000, 1, 'ALI_PAY',
          'PROCESSING',pay.time_delta(), 'SOP1', 'APP', 'MUSIC', 'QQ_MUSIC', '车架号不能为空'),
         ('vin10086', None, 'ex_order001', 'pay001', 'order001', 9999, 10000, 1,  'ALI_PAY','PROCESSING',
          pay.time_delta(), 'SOP1', 'APP', 'MUSIC', 'QQ_MUSIC', 'aid不能为空'),
         ('vin10086', 'aid001', None, 'pay001', 'order001', 9999, 10000, 1, 'ALI_PAY', 'PROCESSING',
          pay.time_delta(), 'SOP1', 'APP', 'MUSIC', 'QQ_MUSIC', '外部订单号不能为空'),
('vin10086', 'aid001', 'ex_order001', None, 'order001', 9999, 10000, 1, 'ALI_PAY', 'PROCESSING',
          pay.time_delta(), 'SOP1', 'APP', 'MUSIC', 'QQ_MUSIC', '外部支付记录号不能为空'),
         ]


@allure.feature('payment')
@allure.story('sync pay stream')
@pytest.mark.payment
@pytest.mark.parametrize('params', error, ids=['不输入车架号','不输入aid','不输入ex_order','不输入pay_no'])
def test_sync_pay_stream_wrong(params):
    '''
    测试同步支付记录，异常情况
    '''

    data = {'vin': params[0], 'aid': params[1], 'exOrderNo': params[2], 'exPayNo': params[3], 'orderNo': params[4],
            'payAmount': params[5], 'orderAmount': params[6], 'discountAmount': params[7], 'payChannel': params[8],
            'payStatus': params[9], 'payTime': params[10], 'origin':params[11],'payWay': params[12], 'serviceId': params[13],
            'spId': params[14]}
    res = pay.sync_pay_stream(data)
    assert res['returnStatus'] == 'FAILED'
    assert res['errorMessage'] == params[15]

