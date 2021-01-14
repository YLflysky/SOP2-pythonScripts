from order.ma_order import MAOrder
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
    order_no = ma.create_order(goods_id=17,category='MUSIC_VIP',aid=aid,quantity=1,point=False,durationTimes=data[0])['data']
    sql_res_payment = ma.do_mysql_select('select * from ORDER_ITEM where orderId="{}"'.format(order_no),'uat_mosc_payment','MA')
    sql_res_order = ma.do_mysql_select('SELECT * FROM ORDER_MASTER WHERE orderNo="{}"'.format(order_no),'uat_mosc_order','MA')
    assert len(sql_res_order) == len(sql_res_payment) == 1
    assert sql_res_payment[0]['goodsName'] == sql_res_order[0]['orderTitle'] == data[-1]
    assert sql_res_payment[0]['orderPrice'] == sql_res_order[0]['actualPayAmount'] == data[1]
    ma.get_ma_qr_code(order_no,'11100')