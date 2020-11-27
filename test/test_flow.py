import pytest
import allure
import random
import sys, os
import json
from flow.flow_api import Flow
from order.payment import Payment
from box.lk_logger import lk

pay = Payment()
flow = Flow()


@allure.suite('flow')
@allure.title('BM车机端获取流量详情测试用例')
@pytest.mark.flow
@pytest.mark.parametrize('id', ['266', '254', '255', '85'])
def test_bm_flow_detail(id):
    res = flow.bm_get_flow_detail(id)
    assert res['code'] == 0
    sql = flow.do_mysql_select('SELECT g.*,f.description,c.goodsStatus from GOODS g,'
                               'FLOW_ATTRIBUTE f,GOODS_CONTROL c where 1=1 and g.id = c.goodsId and '
                               'g.goodsCodes=f.goodsCodes and c.goodsStatus="ALREADY_SHELVES" and g.id={}'.format(id),
                               'fawvw_flow', 'SOP2')
    assert res['data']['goodsName'] == sql[0]['goodsName']
    assert res['data']['descripiton'] == sql[0]['description']
    assert res['data']['termsOfserviceUrl'] == sql[0]['goodsUrl']
    assert res['data']['price'] == sql[0]['goodsPrice']


@allure.suite('flow')
@allure.title('底层获取流量详情测试用例')
@pytest.mark.flow
@pytest.mark.parametrize('goods_id', ['100', '101', '102', '256', '257', '258']
    , ids=['酷我1个月VIP', '酷我3个月VIP', '酷我6个月VIP', '在线媒体月包', '在线媒体季包', 'Wi-Fi半年包'])
def test_flow_detail(goods_id):
    res = flow.flow_detail(goods_id)
    assert res['returnStatus'] == 'SUCCEED'
    assert res['data']['goodsControlStatus'] == 'ALREADY_SHELVES'
    assert res['data']['goodsName']


@pytest.mark.flow
@allure.suite('flow')
@allure.title('用户获取流量列表》》获取流量详情')
@pytest.mark.parametrize('category', ['MUSIC_VIP', 'RADIO_VIP', 'WIFI_FLOW', 'MEDIA_FLOW', 'PAID_CONTENT'])
def test_goods_list_detail(category):
    # 获取WIFI流量列表
    res1 = flow.bm_goods_list('10086', [category])
    for category_list in res1['data']['goodsCategories']:
        assert category_list['category'] == category
        if len(category_list['goods']) > 0:
            for x in category_list['goods']:
                ids = x['goodsId']
                res = flow.bm_get_flow_detail(ids)
                assert res['data']['goodsName']
                assert res['data']['price'] is not None


@allure.suite('flow')
@allure.title('BM车机端获取流量详情')
@pytest.mark.flow
@pytest.mark.parametrize('goods', [None, flow.f.pyint(), '261', '246'],
                         ids=['不输入商品编号', '不存在的编号', '商品已下架', '商品未上架'])
def test_bm_flow_detail_wrong(goods):
    '''
    BM车机端获取流量详情，异常情况
    :return:
    '''
    res = flow.bm_get_flow_detail(goods)
    assert res['code'] != 0


@allure.suite('flow')
@allure.title('免密签约结果回调')
@pytest.mark.flow
@pytest.mark.parametrize('param', [(flow.f.pyint(), 1, 1, 1, 'ALI_PAY', 'OPEN'),
                                   (flow.f.pyint(), 2, 2, 2, 'WECHAT_PAY', 'CLOSE'),
                                   (flow.f.pyint(), 2, 1, 1, 'WECHAT_PAY', 'OPEN'),
                                   (flow.f.pyint(), 1, 2, 2, 'ALI_PAY', 'CLOSE')]
    , ids=['支付宝签约', '微信解约', '微信签约', '支付宝解约'])
def test_sign_result_callback(param):
    res = flow.sign_result_callback(param[0], param[1], param[2], param[3])
    assert res['status'] == '0000_0'
    assert res['messages'][0] == '成功'
    sql = flow.do_mysql_select(
        'select * from contract_sign where aid = "{}" and pay_channel="{}"'.format(param[0], param[4]), 'fawvw_pay')
    assert sql[0]['sign_status'] == param[5]


@allure.suite('flow')
@allure.title('免密签约结果回调')
@pytest.mark.flow
@pytest.mark.parametrize('d', [('221', 1, 1, 2), ('221', 1, 2, 1), ('221', 3, 1, 1)],
                         ids=['状态为未签约，通知类型为签约', '状态为已签约，通知类型为解约', '支付渠道错误'])
def test_sign_result_callback_wrong(d):
    '''
    测试免密签约回调异常情况
    :return:
    '''
    res = flow.sign_result_callback(d[0], d[1], d[2], d[3])
    assert res['status'] == '0000_1'
    assert res['messages'][0] == '失败'


@allure.suite('flow')
@allure.title('免密支付结果回调--支付成功')
@pytest.mark.flow
@pytest.mark.parametrize('channel', ['ALI_PAY', 'WECHAT_PAY'], ids=['支付宝支付成功', '微信支付成功'])
def test_pay_result_callback(channel):
    '''
    测试支付成功回调
    :return:
    '''
    aid = 'qq995939534'
    order_msg = flow.bm_create_flow_order(goods_id='253', aid=aid, vin='LFVSOP2TEST000353',
                                          quantity=1)
    order_no = order_msg['data']['orderNo']
    # 根据流量订单支付
    res = pay.get_qr_code(aid, order_no, channel=channel)
    assert res['returnStatus'] == 'SUCCEED'
    # 获取支付payNo
    pay_no = pay.do_mysql_select('select pay_no from pay_order where order_no="{}" and is_effective=1'.format(order_no),
                                 'fawvw_pay')
    pay_no = pay_no[0]['pay_no']
    success_attr = {'thirdPartyPaymentSerial': 'qq995939534', 'payChannel': channel,
                    'paidTime': flow.time_delta(formatted='%Y%m%d%H%M%S')}
    res = flow.common_callback(id=order_no, category=1, status='1000_00', origin_id=flow.f.md5(),
                               additional_attrs=success_attr)
    assert res['status'] == '000000'
    assert res['messages'][0] == '成功'
    sql = flow.do_mysql_select('select order_status from `order` where order_no="{}"'.format(order_no), 'fawvw_order')
    assert sql[0]['order_status'] == 'PAY_SUCCESS'
    sql = flow.do_mysql_select('select * from order_pay where pay_no="{}"'.format(pay_no), 'fawvw_order')
    assert sql[0]['pay_status'] == 'SUCCESS'
    sql = flow.do_mysql_select('select * from pay_order where pay_no="{}"'.format(pay_no), 'fawvw_pay')
    assert sql[0]['pay_status'] == 'SUCCESS'
    assert sql[0]['pay_channel'] == channel


@allure.suite('flow')
@allure.title('免密支付结果回调--支付失败')
@pytest.mark.flow
def test_pay_result_callback_failed():
    '''
    测试支付失败回调
    :return:
    '''
    aid = 'qq995939534'
    order_msg = flow.bm_create_flow_order(goods_id='253', aid=aid, vin='LFVSOP2TEST000353',
                                          quantity=1)
    order_no = order_msg['data']['orderNo']
    # 根据流量订单支付
    res = pay.get_qr_code(aid, order_no, channel='ALI_PAY')
    assert res['returnStatus'] == 'SUCCEED'
    # 获取支付payNo
    pay_no = pay.do_mysql_select('select pay_no from pay_order where order_no="{}" and is_effective=1'.format(order_no),
                                 'fawvw_pay')
    pay_no = pay_no[0]['pay_no']
    success_attr = {'thirdPartyPaymentSerial': 'qq995939534', 'payChannel': 'ALI_PAY',
                    'paidTime': flow.time_delta(formatted='%Y%m%d%H%M%S')}
    res = flow.common_callback(id=order_no, category=1, status='1000_01', origin_id=flow.f.md5(),
                               additional_attrs=success_attr)
    assert res['status'] == '000000'
    assert res['messages'][0] == '成功'
    sql = flow.do_mysql_select('select order_status from `order` where order_no="{}"'.format(order_no), 'fawvw_order')
    assert sql[0]['order_status'] == 'WAITING_PAY'
    sql = flow.do_mysql_select('select pay_status from pay_order where pay_no="{}"'.format(pay_no), 'fawvw_pay')
    assert sql[0]['pay_status'] == 'FAILED'


@pytest.mark.flow
@allure.suite('flow')
@allure.title('流量底层剩余流量提醒通知')
def test_sim_notify():
    id = flow.f.pyint()
    date = flow.time_delta(formatted='%Y%m%d%H%M%S')
    rule = flow.f.pyfloat(positive=True, min_value=0.0, max_value=1.0)
    asset_type = 'iccid'
    asset_id = flow.f.md5()
    package = 'P1001123577'
    vin = 'LFV2A11KXA3030241'
    res = flow.flow_sim_notify(id, date, rule, asset_type, asset_id, package, vin)
    assert res['messages'][0] == '成功'
    sql = flow.do_mysql_select(
        'select * from mosc_mqtt_message where service_id=8000 order by create_date desc limit 1', 'mosc_mqtt_center')
    assert sql[0]['body']
    body = json.loads(sql[0]['body'])
    assert body['vin'] == vin


@pytest.mark.flow
@pytest.mark.parametrize('channel', ['ALI_PAY', 'WECHAT_PAY'])
@allure.suite('flow')
@allure.title('cp-adapter支付结果回调到ftb2.2')
def test_cp_common_notify_ftb22(channel):
    '''
    测试cp-adapter支付结果回调到ftb2.2
    :return:
    '''
    # 获取流量订单
    aid = 'sergio123'
    flow_order = flow.bm_create_flow_order('253', aid, 'LFVSOP2TEST000353', 1)
    no = flow_order['data']['orderNo']
    # 根据流量订单支付
    res = pay.get_qr_code(aid, no, channel)
    assert res['returnStatus'] == 'SUCCEED'
    # 获取支付payNo
    pay_no = pay.do_mysql_select(
        'select pay_no from pay_order where order_no="{}" and is_effective=1'.format(no), 'fawvw_pay')
    pay_no = pay_no[0]['pay_no']
    # CP回调支付结果，支付成功
    res = flow.cp_common_notify(id=no, category=1, status='1000_00', origin_id=flow.f.md5())
    assert res['status'] == '000000'
    assert res['messages'][0] == '成功'
    sql_res = flow.do_mysql_select('select * from pay_order where pay_no="{}"'.format(pay_no),'fawvw_pay')
    assert sql_res[0]['pay_status'] == 'SUCCESS'
    assert sql_res[0]['ex_pay_no'] == 'qq995939534'


@pytest.mark.flow
@allure.suite('flow')
@allure.title('cp-adapter支付结果回调到sop1')
def test_cp_common_notify_sop1():
    # CP回调支付结果，支付成功
    res = flow.cp_common_notify(id=flow.f.pyint(), category=1, status='1000_00', origin_id=flow.f.md5())
    assert res['status'] == '0000_0'
    assert res['messages'][0] == '成功'


@pytest.mark.flow
@allure.suite('flow')
@allure.title('cp-adapter签约结果回调')
def test_cp_sign_result_notify():
    res = flow.cp_sign_result_notify(user_id=flow.f.pyint(), channel=1, notify_type=1, status=1)
    assert res['status'] == '0000_0'
    assert res['messages'][0] == '成功'


@pytest.mark.flow
@allure.suite('flow')
@allure.title('cp-adapter流量达到阈值提醒回调ftb2.2')
def test_cp_sim_notify_ftb22():
    id = flow.f.pyint()
    date = flow.time_delta(formatted='%Y%m%d%H%M%S')
    rule = flow.f.pyfloat(positive=True, min_value=0.0, max_value=1.0)
    asset_type = 'iccid'
    acc_id = '995939534cmcctest002x'
    package = 'P1001123577'
    res = flow.cp_sim_notify(id, date, rule, asset_type, acc_id, package_id=package)
    assert res['status'] == '000000'
    assert res['messages'][0] == '成功'


@pytest.mark.flow
@allure.suite('flow')
@allure.title('cp-adapter流量达到阈值提醒回调失败场景')
@pytest.mark.parametrize('param', [(1024, '20200101000000', '0.1', 'iccid', '123', 'P1001123577'),
                                   (1024, '20200101000000', '0.1', 'iccid', '102466test001x', 'L123')]
    , ids=['iccid无法获取vin', 'package不存在'])
def test_cp_sim_notify_wrong(param):
    res = flow.cp_sim_notify(param[0], param[1], param[2], param[3], param[4], param[5])
    if 'returnStatus' in res.keys():
        assert res['returnStatus'] == 'FAILED'
    elif 'status' in res.keys():
        assert res['status'] == '0000_1'
