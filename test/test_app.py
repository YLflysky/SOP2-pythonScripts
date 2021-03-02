import pytest
import allure
import random
from box.lk_logger import lk
from .conftest import app,vins,aid,bm_order
from app.app_api import App


event_id = random.randint(10000, 100000)
event = {'localEventId':event_id , 'cudStatus': 'C','rrule':'Only Once',
                     'eventStartTime': app.get_time_stamp(days=-1), 'eventEndTime': app.get_time_stamp(days=1)}


def assert_results():
    '''
    查询数据库看是否同步成功
    :return:
    '''
    sql_res = app.do_mysql_select('SELECT * from calendar_event where uid="{}" and local_event_id="{}"'.format(aid,event_id),'fawvw_calendar')
    try:
        assert len(sql_res) == 1
    finally:
        app.do_mysql_exec('delete from calendar_event where uid="{}" and local_event_id="{}"'.format(aid,event_id),'fawvw_calendar')


@allure.suite('app')
@allure.title('测试传入vin判断车型，然后通过APP同步日历事件')
@pytest.mark.app
@pytest.mark.parametrize('vin',vins)
def test_app_sync_event(vin):
    lk.prt(vin)
    vin_code = vin[0]
    tenant = vin[1]
    assert app.get_tenant_by_vin(vin_code) == tenant
    lk.prt('check {} tenant success'.format(tenant))
    res = app.calendar_mobile_sync(current_time=None,events=[event],vin=vin_code)
    if tenant in ('SOP2BM','SOP2MA'):
        assert_results()


@allure.suite('app')
@allure.title('测试传入vin判断车型，然后查询所有日历事件')
@pytest.mark.app
@pytest.mark.parametrize('vin',vins[:2])
def test_app_calendar_find_all(vin):
    res = app.calendar_mobile_find_all(vin=vin[0])
    assert res['data']


@allure.suite('app')
@allure.title('测试传入用户没有绑定的vin ,调用app接口失败')
@pytest.mark.app
def test_app_vin_wrong():
    res = app.calendar_mobile_find_all(vin='LFVSOP2TEST00033100')
    assert res['errorCode'] == 'ACO0004'


@allure.suite('app')
@allure.title('测试查询CMCC未签约结果')
@pytest.mark.app
def test_app_cmcc_unsign():
    res = app.get_sign_result(vin='LFVSOP2TESTLY0002',channel='WXPAY',cp_seller='CMCC')
    assert res['data']['signNo'] == '2'


@allure.suite('app')
@allure.title('测试查询CMCC已签约结果')
@pytest.mark.app
def test_app_cmcc_sign():
    app_sign = App(name='13770614790',password='000000',aid='9350963')
    res = app_sign.get_sign_result(vin='LFVSOP2TESTLY0002',channel='WXPAY',cp_seller='CMCC')
    assert res['data']['signNo'] == '1'


@allure.suite('app')
@allure.title('测试APP获取流量订单支付URL')
@pytest.mark.app
@pytest.mark.parametrize('channel',['QR_ALIPAY','QR_WEIXIN'])
def test_app_pay_url_flow(channel):
    vin = 'LFVSOP2TEST000353'
    order_no = app.create_order(goods_id='253',category='MEDIA_FLOW',vin=vin,count=1)['data']['orderNumber']
    res = app.get_pay_url(order_no,channel)
    assert res['data']['payUrl']


@allure.suite('app')
@allure.title('测试APP获取音乐订单支付URL')
@pytest.mark.app
@pytest.mark.parametrize('channel',['QR_ALIPAY','QR_WEIXIN'])
def test_app_pay_url_music(channel):
    vin = 'LFVSOP2TEST000353'
    order_no = app.create_order(goods_id='253',category='MEDIA_FLOW',vin=vin,count=1)['data']['orderNumber']
    res = app.get_pay_url(order_no,channel)
    assert res['data']['payUrl']


@allure.suite('app')
@allure.title('测试APP获取电台订单支付URL')
@pytest.mark.app
@pytest.mark.parametrize('channel',['QR_ALIPAY','QR_WEIXIN'])
def test_app_pay_url_radio(channel):
    aid = '4614931'
    vin = 'LFVSOP2TEST000353'
    order_no = bm_order.goods_order_create(tenant_id='VW',aid=aid,vin=vin,goods='273',quantity=1)['data']['orderNo']
    res = app.get_pay_url(order_no,channel)
    assert res['data']['payUrl']







