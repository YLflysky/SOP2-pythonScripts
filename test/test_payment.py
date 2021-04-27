import pytest
from .conftest import pay
from .conftest import bm_order, ma_order, sop1_order,ma_pay
import allure
from box.lk_logger import lk


@allure.suite('payment')
@allure.title('获取支付结果')
@pytest.mark.payment
@pytest.mark.parametrize('d', [('ftb20201202112131435753664', '9351499', 'SUCCESS'),
                               ('ftb20201127151324000753664', 'qq995939534', 'FAILED'),
                               ('20200907105829249819204', '32432', 'PROCESSING')],
                         ids=['支付成功', '支付失败', '支付中'])
def test_get_pay_result(d):
    res = pay.get_pay_result(order_no=d[0], aid=d[1])
    sql = pay.do_mysql_select('select * from pay_order where order_no="{}" order by pay_time desc limit 1'.format(d[0]),
                              'fawvw_pay')
    if sql[0]['buyer_account']:
        assert res['data']['buyerAccount'] == sql[0]['buyer_account']
    status = sql[0]['pay_status']
    assert status == d[-1]


@allure.suite('payment')
@allure.title('获取支付结果异常情况')
@pytest.mark.payment
@pytest.mark.parametrize('d', [(pay.f.pyint(), '123', 'Feign调用order获取订单数据错误'),
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
@allure.title('获取支付协议')
@pytest.mark.payment
@pytest.mark.parametrize('d', [('9642113', '11112223', '11101', 'en-US', 'ENGLISH'),
                               ('9351524', '111124424523', '12101', 'zh-CN', 'QQ音乐')]
    , ids=['支付宝英文协议', '微信中文协议'])
def test_get_pay_agreement(d):
    '''
    测试获取支付协议
    '''
    res = pay.get_pay_agreement(uid=d[0], code=d[2], order_no=d[1], lang=d[3])
    assert res['data']['title'] == d[-1]


@allure.suite('payment')
@allure.title('获取支付协议')
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
@allure.title('获取支付协议')
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


@allure.suite('payment')
@allure.title('支付宝cdp回调')
@pytest.mark.payment
@pytest.mark.skip()
def test_ali_pay_cdp_callback_01():
    '''
    测试获取支付宝cdp回调结果，输入全部必填项
    '''
    # 创建订单
    xmly_aid = '9354046'
    vin = 'LFVSOP2TESTLY0073'
    order_no = bm_order.goods_order_create(tenant_id='VW', aid=xmly_aid, vin=vin, goods='234', quantity=1)['data'][
        'orderNo']
    # 获取支付二维码，生成支付记录
    pay_msg = pay.get_qr_code(xmly_aid, order_no, 'ALI_PAY')
    pay_no = pay.do_mysql_select(
        'select pay_no from pay_order where order_no="{}" and is_effective=1'.format(order_no),
        'fawvw_pay')
    pay_no = pay_no[0]['pay_no']
    amount = pay_msg['data']['payAmount']
    pay_time = pay.time_delta()
    trade_no = pay.f.md5()
    # 回调支付结果
    res = pay.ali_pay_callback(pay_no, amount, pay_time, trade_no)
    try:
        assert res == 'success'
        # 检查支付结果同步到支付记录中
        res = pay.get_pay_result(order_no, xmly_aid)
        assert res['data']['payResultStatus'] == '101'
        # 检查支付结果同步到订单中
        pay_res = pay.do_mysql_select('select * from order_pay where pay_no="{}"'.format(pay_no), 'fawvw_order')
        assert pay_res[0]['pay_channel'] == 'ALI_PAY'
        assert pay_res[0]['pay_way'] == 'QR_PAY'
        assert float(pay_res[0]['pay_amount']) == float(amount)
        assert pay_res[0]['pay_time'] == pay_time
        assert pay_res[0]['pay_status'] == 'SUCCESS'
    finally:
        pay.do_mysql_exec('delete from order_pay where order_no="{}"'.format(order_no), 'fawvw_order')
        pay.do_mysql_exec('delete from pay_order where order_no="{}" and is_effective=1'.format(order_no), 'fawvw_pay')
        pay.do_mysql_exec('delete from `order` where order_no="{}"'.format(order_no), 'fawvw_order')


@allure.suite('payment')
@allure.title('支付宝cdp回调')
@pytest.mark.payment
@pytest.mark.skip()
def test_ali_pay_cdp_callback_02():
    '''
    测试获取支付宝cdp回调结果，回调参数加上选填项
    '''
    # 创建喜马拉雅VIP订单
    xmly_aid = '9354046'
    vin = 'LFVSOP2TESTLY0073'
    order_no = bm_order.goods_order_create(tenant_id='VW', aid=xmly_aid, vin=vin, goods='234', quantity=1)['data'][
        'orderNo']

    # 获取支付二维码，生成支付记录
    pay_msg = pay.get_qr_code(xmly_aid, order_no, 'ALI_PAY')
    pay_no = pay.do_mysql_select('select pay_no from pay_order where order_no="{}" and is_effective=1'.format(order_no),
                                 'fawvw_pay')
    pay_no = pay_no[0]['pay_no']
    receipt_amount = 99.99
    gmt_payment = pay.time_delta(days=-1)
    trade_no = '10000'
    seller_email = pay.f.email()
    buyer_logon_id = pay.f.email()
    seller_id = pay.f.pyint(10000, 10000000)
    buyer_id = pay.f.pyint(10000, 10000000)
    total = 100.00
    res = pay.ali_pay_callback(pay_no, receipt_amount, gmt_payment, trade_no,
                               buyer_logon_id=buyer_logon_id, total_amount=total, seller_id=seller_id,
                               seller_email=seller_email, buyer_id=buyer_id)
    try:
        assert res == 'success'
        # 校验支付结果同步到订单支付结果中
        pay_res = pay.do_mysql_select('select * from order_pay where pay_no="{}"'.format(pay_no), 'fawvw_order')
        assert pay_res[0]['pay_channel'] == 'ALI_PAY'
        assert pay_res[0]['pay_no'] == pay_no
        assert pay_res[0]['pay_way'] == 'QR_PAY'
        assert pay_res[0]['pay_amount'] == receipt_amount
        assert pay_res[0]['pay_time'] == gmt_payment
        # 校验支付结果同步到支付的支付记录中
        res = pay.get_pay_result(order_no, xmly_aid)
        assert res['data']['buyerAccount'] == buyer_logon_id
        assert res['data']['payResultStatus'] == '101'
    finally:
        pay.do_mysql_exec('delete from order_pay where order_no="{}"'.format(order_no), 'fawvw_order')
        pay.do_mysql_exec('delete from pay_order where order_no="{}" and is_effective=1'.format(order_no), 'fawvw_pay')
        pay.do_mysql_exec('delete from `order` where order_no="{}"'.format(order_no), 'fawvw_order')


@allure.suite('payment')
@allure.title('支付宝cdp回调SOP1')
@pytest.mark.payment
@pytest.mark.skip("不能连接数据库")
def test_ali_pay_cdp_callback_sop1():
    '''
    输入的out_trade_no不在FTB2.2数据库中查询到，调用SOP1的service
    '''
    aid = '4614183'
    vin = 'LFVTEST1231231231'
    order_no = sop1_order.sop1_create_order(aid=aid, goods_id='17', category='MUSIC_VIP', quantity=1, point=False,
                                            durationDays=1, vin=vin)['data']['orderNumber']
    sop1_order.get_qr_code(vin, order_no=order_no, pay_type='11100', aid=aid)
    out_trade_no = ma_order.do_mysql_select(
        'select tempOrderId from ORDER_ID_RELATION where orderId="{}"'.format(order_no), 'uat_mosc_payment', 'MA')
    assert len(out_trade_no) == 1
    out_trade_no = out_trade_no[0]['tempOrderId']
    receipt_amount = 99.99
    gmt_payment = pay.time_delta(days=-1)
    trade_no = '10000'
    res = pay.ali_pay_callback(out_trade_no, receipt_amount, gmt_payment, trade_no, )
    assert res == 'success'
    try:
        pay_res = pay.do_mysql_select('select * from ORDER_ITEM where orderId="{}"'.format(order_no), 'uat_mosc_payment','MA')
        assert pay_res[0]['orderStatus'] == 'FINISHED'
        assert pay_res[0]['payTime'] == gmt_payment
        # 校验支付结果同步到支付的支付记录中
        res = ma_order.do_mysql_select('select * from PAY_ORDER where orderNo="{}"'.format(order_no),'uat_mosc_payment','MA')
        assert res[0]['payState'] == 'ALREADY_PAID'
        assert res[0]['payChannel'] == 'ALIPAY'
    finally:
        pass


@allure.suite('payment')
@allure.title('支付宝cdp回调SOP2MA')
@pytest.mark.payment
@pytest.mark.skip("不能连接数据库")
def test_ali_pay_cdp_callback_sop2ma():
    '''
    输入的out_trade_no为sop2ma订单的
    '''
    order_no = ma_order.create_goods_order(aid='4614183', goods_id='17', category='MUSIC_VIP', quantity=1, point=False,
                                           durationTimes=1, vin='LFVTEST1231231231')['data']
    ma_pay.get_qr_code(aid='4614183',vin='LFVTEST1231231231',order_no=order_no, pay_type='11100',category='01')
    out_trade_no = ma_order.do_mysql_select(
        'select tempOrderId from ORDER_ID_RELATION where orderId="{}"'.format(order_no), 'uat_mosc_payment', 'MA')
    assert len(out_trade_no) == 1
    out_trade_no = out_trade_no[0]['tempOrderId']
    receipt_amount = 99.99
    gmt_payment = pay.time_delta(days=-1)
    trade_no = '10000'
    res = pay.ali_pay_callback(out_trade_no, receipt_amount, gmt_payment, trade_no, )
    assert res == 'success'
    try:
        pay_res = pay.do_mysql_select('select * from ORDER_MASTER where orderNo="{}"'.format(order_no), 'uat_mosc_order','MA')
        assert pay_res[0]['orderStatus'] == 'FINISHED'
        assert pay_res[0]['payTime'] == gmt_payment
        assert pay_res[0]['payWay'] == 'QR_CODE'
        assert pay_res[0]['actualPayAmount'] == receipt_amount
        # 校验支付结果同步到支付的支付记录中
        res = ma_order.do_mysql_select('select * from PAY_ORDER where orderNo="{}"'.format(order_no),'uat_mosc_pay','MA')
        assert res[0]['payStatus'] == 'SUCCESS'
        assert res[0]['payChannel'] == 'ALIPAY'
    finally:
        pass


callback_data_fail = [(None, '1.00', pay.time_delta()),
                      ('ftb123', None, pay.time_delta()),
                      ('ftb123', '1.00', None)]


@allure.suite('payment')
@allure.title('支付宝cdp回调异常情况')
@pytest.mark.payment
@pytest.mark.parametrize('d', callback_data_fail, ids=['没传out_trade_no', '没传回调金额', '没传支付时间'])
def test_ali_pay_cdp_callback_wrong(d):
    '''
    测试获取支付宝cdp回调结果，异常情况测试
    '''

    res = pay.ali_pay_callback(out_trade_no=d[0], receipt_amount=d[1],gmt_payment=d[2],trade_no='123')
    assert res == 'failure'


@allure.suite('payment')
@allure.title('免密签约结果回调')
@pytest.mark.payment
@pytest.mark.parametrize('d', [('ALI_PAY', 'OPEN', 'OPEN'), ('ALI_PAY', 'CLOSE', 'PAUSE'),
                               ('WECHAT_PAY', 'OPEN', 'OPEN'), ('WECHAT_PAY', 'CLOSE', 'PAUSE')]
    , ids=['支付宝签约', '支付宝解约', '微信签约', '微信解约'])
def test_flow_sign_notify(d):
    '''
    测试回调免密支付结果接口--CMCC流量业务免密
    '''
    aid = '9354046'
    pay.contract_sign_notify(aid, service='FLOW', operator='270001', channel=d[0], sign_status=d[1], pause_status=d[2])
    try:
        sql = pay.do_mysql_select('select * from contract_sign where aid="{}" and pay_channel="{}"'.format(aid, d[0]),
                                  'fawvw_pay')
        assert sql[0]['pause_status'] == d[2]
        assert sql[0]['sign_status'] == d[1]
    finally:
        pay.do_mysql_exec('delete from contract_sign where aid="{}" and pay_channel="{}"'.format(aid, d[0]),
                          'fawvw_pay')


@allure.suite('payment')
@allure.title('免密签约结果回调异常情况')
@pytest.mark.payment
@pytest.mark.parametrize('wrong', [('221', None, 'OPEN', 'PAUSE'), ('221', 'ALI_PAY', None, 'OPEN'),
                                   ('221', 'ALI_PAY1', 'OPEN', 'OPEN'),
                                   ('221', 'ALI_PAY', 'OPEN1', 'OPEN'), ('221', 'ALI_PAY', 'OPEN', 'OPEN1'),
                                   (None, 'ALI_PAY', 'OPEN', 'OPEN')],
                         ids=['不输入channel', '不输入签约状态', '输入channel错误', '输入签约状态错误', '输入开启关闭状态错误', '不输入aid'])
def test_cmcc_callback_wrong(wrong):
    '''
    测试回调免密支付结果接口--异常情况
    '''
    res = pay.contract_sign_notify(aid=wrong[0], service='FLOW', operator='270001', channel=wrong[1],
                                   sign_status=wrong[2], pause_status=wrong[3])
    assert res['returnStatus'] == 'FAILED'


@allure.suite('payment')
@allure.title('同步支付记录')
@pytest.mark.payment
@pytest.mark.parametrize('enum', [('ALI_PAY', 'PROCESSING', 'QR_PAY', 'BM'),
                                  ('WECHAT_PAY', 'SUCCESS', 'APP', 'MA'),
                                  ('WECHAT_PAY', 'FAILED', 'FREE_PASS_PAY', 'SOP1'),
                                  ('WECHAT_PAY', 'SUCCESS', 'ALL_DEDUCTION', 'SOP1'),
                                  ('UNKNOWN', 'FAILED', 'FREE_PASS_PAY', 'SELF')]
    , ids=['支付宝-支付中-二维码-BM', '微信-支付成功-APP-MA', '微信-支付失败-免密-SOP1', '微信-支付成功-全额抵扣-SOP1','未知渠道-支付失败-免密-SELF'])
def test_sync_pay_result(enum):
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
    sp_id = 'KUWO'
    data = {'vin': vin, 'aid': aid, 'exOrderNo': ex_order, 'exPayNo': ex_pay_no, 'orderNo': order_no,
            'payAmount': pay_amount, 'orderAmount': order_amount, 'discountAmount': discount, 'payChannel': channel,
            'payStatus': status, 'payTime': pay_time, 'payWay': pay_way, 'serviceId': service_id, 'spId': sp_id,
            'origin': origin}
    pay.sync_pay_stream(data)
    try:
        sql_res = pay.do_mysql_select('select * from pay_order where ex_pay_no="{}"'.format(ex_pay_no), 'fawvw_pay')
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
        pay.do_mysql_exec('delete from pay_order where ex_pay_no="{}"'.format(ex_pay_no), 'fawvw_pay')


@allure.suite('payment')
@allure.title('同步支付记录')
@pytest.mark.payment
@pytest.mark.parametrize('status', ['INIT', 'WAIT_BUYER_PAY', 'TRADE_SUCCESS', 'TRADE_CLOSED', 'TRADE_FINISHED'])
def test_sync_pay_stream_xuantian(status):
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
    origin = 'BM'
    pay_way = 'APP'
    service_id = 'MUSIC'
    sp_id = 'KUWO'
    buyer = pay.f.email()
    reason = pay.f.sentence()
    data = {'vin': vin, 'aid': aid, 'exOrderNo': ex_order, 'exPayNo': ex_pay_no, 'orderNo': order_no,
            'payAmount': pay_amount, 'orderAmount': order_amount, 'discountAmount': discount, 'payChannel': channel,
            'payStatus': status, 'payTime': pay_time, 'payWay': pay_way, 'serviceId': service_id, 'spId': sp_id,
            'origin': origin,
            'buyerAccount': buyer, 'failReason': reason}
    pay.sync_pay_stream(data)
    try:
        sql_res = pay.do_mysql_select('select * from pay_order where ex_pay_no="{}"'.format(ex_pay_no), 'fawvw_pay')
        assert len(sql_res) == 1
        sql_res = sql_res[0]
        assert sql_res['pay_status'] == status
        assert sql_res['buyer_account'] == buyer
        assert sql_res['fail_reason'] == reason
    finally:
        pay.do_mysql_exec('delete from pay_order where ex_pay_no="{}"'.format(ex_pay_no), 'fawvw_pay')


@allure.suite('payment')
@allure.title('同步支付记录')
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
        sql_res = pay.do_mysql_select('select * from pay_order where ex_pay_no="{}"'.format(ex_pay_no), 'fawvw_pay')
        assert len(sql_res) == 1
        sql_res = sql_res[0]
        assert sql_res['buyer_account'] == buyer
        assert sql_res['fail_reason'] == reason
    finally:
        pass


error = [(None, 'aid001', 'ex_order001', 'pay001', 'order001', 9999, 10000, 1, 'ALI_PAY',
          'PROCESSING', pay.time_delta(), 'SOP1', 'APP', 'MUSIC', 'QQ_MUSIC', '车架号不能为空'),
         ('vin10086', None, 'ex_order001', 'pay001', 'order001', 9999, 10000, 1, 'ALI_PAY', 'PROCESSING',
          pay.time_delta(), 'SOP1', 'APP', 'MUSIC', 'QQ_MUSIC', '用户aid不能为空'),
         ('vin10086', 'aid001', None, 'pay001', 'order001', 9999, 10000, 1, 'ALI_PAY', 'PROCESSING',
          pay.time_delta(), 'SOP1', 'APP', 'MUSIC', 'QQ_MUSIC', '外部订单号不能为空'),
         ('vin10086', 'aid001', 'ex_order001', None, 'order001', 9999, 10000, 1, 'ALI_PAY', 'PROCESSING',
          pay.time_delta(), 'SOP1', 'APP', 'MUSIC', 'QQ_MUSIC', '外部支付记录号不能为空'),
         ]


@allure.suite('payment')
@allure.title('同步支付记录')
@pytest.mark.payment
@pytest.mark.parametrize('params', error, ids=['不输入车架号', '不输入aid', '不输入ex_order', '不输入pay_no'])
def test_sync_pay_stream_wrong(params):
    '''
    测试同步支付记录，异常情况
    '''

    data = {'vin': params[0], 'aid': params[1], 'exOrderNo': params[2], 'exPayNo': params[3], 'orderNo': params[4],
            'payAmount': params[5], 'orderAmount': params[6], 'discountAmount': params[7], 'payChannel': params[8],
            'payStatus': params[9], 'payTime': params[10], 'origin': params[11], 'payWay': params[12],
            'serviceId': params[13],
            'spId': params[14]}
    res = pay.sync_pay_stream(data)
    assert res['returnStatus'] == 'FAILED'
    assert res['errorMessage'] == params[15]


@allure.suite('payment')
@allure.title('同步支付结果')
@pytest.mark.payment
def test_sync_pay_result():
    '''
    测试同步支付结果：生成二维码->支付成功->支付宝或微信同步支付结果
    :return:
    '''
    pay.get_qr_code(aid='9642113', order_no='orderNo0001', channel='ALI_PAY')
    no = pay.do_mysql_select('select pay_no from pay_order where order_no="orderNo0001" and is_effective=1',
                             'fawvw_pay')
    no = no[0]['pay_no']
    ex_no = pay.f.pyint(100000, 1000000)
    time = pay.time_delta()
    amount = pay.f.pyfloat(positive=True, right_digits=2, left_digits=4)
    res = pay.sync_pay_result(pay_no=no, ex_pay_no=ex_no, pay_time=time, amount=amount, origin='BM', channel='ALI_PAY',
                              way='QR_PAY', status='SUCCESS')
    try:
        assert res['returnStatus'] == 'SUCCEED'
        sql_pay = pay.do_mysql_select('select * from pay_order where pay_no="{}"'.format(no), 'fawvw_pay')
        assert sql_pay[0]['pay_status'] == 'SUCCESS'
        assert sql_pay[0]['pay_amount'] == amount
        print('支付流水断言成功')
        sql_order = pay.do_mysql_select('select * from order_pay where pay_no="{}"'.format(no), 'fawvw_order')
        assert len(sql_order) == 1
        assert sql_order[0]['pay_status'] == 'SUCCESS'
        assert sql_order[0]['pay_amount'] == amount
        print('订单结果断言成功')
    finally:
        pay.do_mysql_exec('delete from order_pay where order_no="orderNo0001"', 'fawvw_order')
        pay.do_mysql_exec('delete from pay_order where order_no="orderNo0001" and is_effective=1', 'fawvw_pay')


@allure.suite('payment')
@allure.title('测试获取流量订单支付url')
@pytest.mark.payment
@pytest.mark.parametrize('channel', ['ALI_PAY', 'WECHAT_PAY'])
def test_get_flow_pay_url(channel):
    aid = '9354046'
    vin = 'LFVSOP2TEST000353'
    order_no = bm_order.goods_order_create(tenant_id='VW', aid=aid, vin=vin, goods='253', quantity=1)['data']['orderNo']
    res = pay.get_qr_code(aid, order_no, channel, payWay='APP')
    assert res['data']['payUrl']


@allure.suite('payment')
@allure.title('测试获取电台订单支付url')
@pytest.mark.payment
@pytest.mark.parametrize('channel', ['ALI_PAY', 'WECHAT_PAY'])
def test_get_radio_pay_url(channel):
    aid = '4614931'
    vin = 'LFVSOP2TEST000353'
    order_no = bm_order.goods_order_create(tenant_id='VW', aid=aid, vin=vin, goods='273', quantity=1)['data']['orderNo']
    res = pay.get_qr_code(aid, order_no, channel, payWay='APP')
    assert res['data']['payUrl']


@allure.suite('payment')
@allure.title('测试获取免密签约url,APP使用，业务为BM')
@pytest.mark.payment
def test_get_sign_url():
    aid = '9351304'
    vin = 'LFVSOP2TESTLY0073'
    res = pay.agreement_qr_code(aid, channel='ALI_PAY', origin='BM', vin=vin, payWay='APP')
    assert res['data']['appSignUrl']


@allure.suite('payment')
@allure.title('测试查询免密签约状态，业务为BM')
@pytest.mark.payment
def test_get_sign_status():
    aid = '9351304'
    vin = 'LFVSOP2TESTLY0073'
    res = pay.get_sign_result(aid, channel='ALI_PAY', origin='BM', vin=vin)
    assert res['data'] == False


@allure.suite('payment')
@allure.title('测试获取免密签约二维码,车机端使用，业务为BM')
@pytest.mark.payment
@pytest.mark.skip(reason='不支持车机端')
def test_get_sign_qr_code():
    aid = '9351304'
    vin = 'LFVSOP2TESTLY0073'
    res = pay.agreement_qr_code(aid, channel='ALI_PAY', origin='BM', vin=vin, payWay='QR_PAY')
    assert res['data']['appSignUrl']
