from ma_api.ma_order import MAOrder
import pytest
import allure

ma = MAOrder(aid='4614183',user='15330011918',password='000000',vin='LFVTEST1231231231')


@pytest.mark.ma_order
@allure.suite('ma_order')
@allure.title('创建MA音乐vip订单')
@pytest.mark.parametrize('data',[(1,19.9,'酷我VIP-1个月'),(3,57,'酷我VIP-3个月'),
                                 (6,108,'酷我VIP-6个月'),(12,204,'酷我VIP-12个月')],
                         ids=['1个月vip','三个月vip','六个月vip','12个月vip'])
@pytest.mark.skip(reason='无法连接MA数据库')
def test_create_music_vip(data):
    aid = ma.aid
    order_no = ma.create_order(goods_id=17,category='MUSIC_VIP',aid=aid,quantity=1,point=False,durationTimes=data[0],vin=ma.vin)['data']
    sql_res_payment = ma.do_mysql_select('select * from ORDER_ITEM where orderId="{}"'.format(order_no),'uat_mosc_payment','MA')
    sql_res_order = ma.do_mysql_select('SELECT * FROM ORDER_MASTER WHERE orderNo="{}"'.format(order_no),'uat_mosc_order','MA')
    assert len(sql_res_order) == len(sql_res_payment) == 1
    assert sql_res_payment[0]['goodsName'] == sql_res_order[0]['orderTitle'] == data[-1]
    assert sql_res_payment[0]['orderPrice'] == sql_res_order[0]['actualPayAmount'] == data[1]
    ma.get_ma_qr_code(order_no,'11100')

@pytest.mark.ma_order
@allure.suite('ma_order')
@allure.title('权益开通后,更改订单状态为FINISHED')
@pytest.mark.skip(reason='无法连接MA数据库')
def test_update_status_finish():
    order_no = ma.create_order(goods_id=17,category='MUSIC_VIP',aid=ma.aid,quantity=1,point=False,durationTimes=1,vin=ma.vin)['data']
    ma.update_status_finish(order_no)
    sql_res = ma.do_mysql_select('select * from ORDER_MASTER WHERE orderNo="{}"'.format(order_no),'uat_mosc_order','MA')
    try:
        assert sql_res[0]['orderStatus'] == 'FINISHED'
    finally:
        ma.do_mysql_exec('delete from ORDER_MASTER WHERE orderNo="{}"'.format(order_no),'uat_mosc_order','MA')


@pytest.mark.ma_order
@allure.suite('ma_order')
@allure.title('更改订单业务状态')
@pytest.mark.skip(reason='无法连接MA数据库')
def test_update_status_finish():
    order_no = ma.create_order(goods_id=17,category='MUSIC_VIP',aid=ma.aid,quantity=1,point=False,durationTimes=1,vin=ma.vin)['data']
    ma.update_business(order_no,status='JOJO',desc='NOTHING_TO_WORRY_ABOUT')
    sql_res = ma.do_mysql_select('select * from ORDER_MASTER WHERE orderNo="{}"'.format(order_no),'uat_mosc_order','MA')
    try:
        assert sql_res[0]['businessStatus'] == 'JOJO'
        assert sql_res[0]['businessStatusDesc'] == 'NOTHING_TO_WORRY_ABOUT'
    finally:
        ma.do_mysql_exec('delete from ORDER_MASTER WHERE orderNo="{}"'.format(order_no), 'uat_mosc_order', 'MA')

@pytest.mark.ma_order
@allure.suite('ma_order')
@allure.title('测试MA加油业务JDO解约失败，因为未签约')
def test_ma_jdo_unsign_failed():

    res = ma.ma_release_sign(channel='ALIPAY',service='03',operator='030003')
    assert res['status'] == 'FAILED'
    assert res['extMessage'] == '免密解约失败'


@pytest.mark.ma_order
@allure.suite('ma_order')
@allure.title('测试MA加油业务JDO签约结果为未签约')
def test_get_ma_jdo_unsign_result():
    res = ma.ma_get_sign_result(channel='ALIPAY', service='03', operator='030003')
    assert res['data'] == '0'


@pytest.mark.ma_order
@allure.suite('ma_order')
@allure.title('测试MA加油业务JDO获取签约地址')
def test_get_ma_jdo_sign():
    res = ma.ma_contract_sign(channel='ALIPAY', service='03', operator='030003')
    assert res['status'] == 'SUCCEED'
    assert 'alipay_sdk' in res['data']['signString']
