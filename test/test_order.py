import pytest
from .conftest import order
import random
import time
import json
import allure
import sys




@allure.suite('order')
@allure.title('生成一个订单号')
@pytest.mark.order
def test_generate_order_no():
    body = order.generate_order_no()
    assert 'SUCCEED' == body['returnStatus']
    assert body['data'] is not None


@allure.suite('order')
@allure.title('同步支付结果')
@pytest.mark.order
def test_sync_pay():
    '''
    测试同步支付结果
    '''
    sql = order.do_mysql_select('select aid,order_no from  `order` where del_flag=0 and order_status="WAITING_PAY"', 'fawvw_order')
    sql = random.choice(sql)
    aid = sql['aid']
    order_no = sql['order_no']
    pay_no = order.f.md5()
    order.sync_order_pay(pay_no,aid=aid,order_no=order_no,pay_status='SUCCESS',channel='ALI_PAY')
    res = order.do_mysql_select('select count(1) from order_pay where pay_no = "{}"'.format(pay_no), 'fawvw_order')
    assert len(res) == 1
    order.do_mysql_exec('delete from order_pay where pay_no="{}"'.format(pay_no), 'fawvw_order')


@allure.suite('order')
@allure.title('callback同步订单信息')
@pytest.mark.order
def test_callback_order():
    ep_order = '123456789'
    info = {'name': 'waka waka', 'age': 18}

    order.sync_order_kafka(ep_order, info, cp="NX_ENGINE",tenant='ASTERIX')
    time.sleep(2.0)
    try:
        sql_res = order.do_mysql_select(
            'select d.detail,o.* '
            'from `order` o,order_detail d where o.order_no=d.order_no and o.ex_order_no="{}"'.format(
                ep_order), 'fawvw_order')
        print('同步订单成功')
        assert len(sql_res) == 1
        assert sql_res[0]['order_status'] == 'WAITING_PAY'
        assert sql_res[0]['business_status'] == 'WAITING_PAY'
        assert sql_res[0]['business_status_desc'] == 'zdh测试'
        assert sql_res[0]['vin'] == 'DEFAULT_VIN'
        assert sql_res[0]['category'] == '105'
        assert sql_res[0]['sp_id'] == 'NX_ENGINE'
        assert sql_res[0]['service_id'] == 'GAS'
        assert str(sql_res[0]['total_amount']) == '6.0'
        assert sql_res[0]['ex_order_no'] == ep_order
        print('同步订单ex_order_no成功:{}'.format(ep_order))
        info = json.dumps(info, sort_keys=True)
        assert sql_res[0]['detail'] == info
        print("同步business info成功：{}".format(info))
    finally:
        order_no = sql_res[0]['order_no']
        order.do_mysql_exec('delete from `order` where order_no="{}"'.format(order_no), 'fawvw_order')
        order.do_mysql_exec('delete from order_detail where order_no="{}"'.format(order_no), 'fawvw_order')



@allure.suite('order')
@allure.title('同步订单信息')
@pytest.mark.order
@pytest.mark.parametrize('order_status', ['INIT', 'WAITING_PAY', 'PROCESSING', 'REFUND_FAILED', 'REFUND_SUCCESS',
                                          'PAY_SUCCESS', 'PAY_FAILED', 'CANCEL', 'FINISH', 'EXPIRE', 'REFUNDING',
                                          'RESERVED'])
def test_sync_order_01(order_status):
    '''
    同步订单接口测试，订单状态枚举
    '''
    ex = 'test001'
    origin = 'EP'
    aid = '123456'
    category = '102'
    res = order.sync_order(ex, origin, aid, category, orderStatus=order_status, timeout=20)
    sql_res = order.do_mysql_select('select order_status from `order` where order_no="{}"'.format(res['data']), 'fawvw_order')
    assert len(sql_res) == 1
    assert sql_res[0]['order_status'] == order_status
    order.do_mysql_exec('delete from `order` where order_no="{}"'.format(res['data']), 'fawvw_order')


@allure.suite('order')
@allure.title('同步订单信息')
@pytest.mark.order
@pytest.mark.parametrize('order_type', ['COMMODITY', 'BUSINESS'])
def test_sync_order_02(order_type):
    '''
    同步订单接口测试，订单类型枚举
    '''
    ex = 'test001'
    origin = 'EP'
    aid = '123456'
    category = '102'
    res = order.sync_order(ex, origin, aid, category, orderType=order_type, checkFlag=True)
    sql_res = order.do_mysql_select('select * from `order` where order_no="{}"'.format(res['data']), 'fawvw_order')
    assert len(sql_res) == 1
    order.do_mysql_exec('delete from `order` where order_no="{}"'.format(res['data']), 'fawvw_order')


@allure.suite('order')
@allure.title('同步订单信息')
@pytest.mark.order
@pytest.mark.parametrize('origin', ['SELF', 'EP', 'BM', 'MA', 'VPA', 'OTHER'])
def test_sync_order_03(origin):
    '''
    同步订单接口测试，订单来源枚举
    '''
    ex = 'test001'
    aid = '123456'
    category = '102'
    res = order.sync_order(ex, origin, aid, category)
    sql_res = order.do_mysql_select('select origin from `order` where order_no="{}"'.format(res['data']), 'fawvw_order')
    assert len(sql_res) == 1
    assert sql_res[0]['origin'] == origin
    order.do_mysql_exec('delete from `order` where order_no="{}"'.format(res['data']), 'fawvw_order')


@allure.suite('order')
@allure.title('同步订单信息>>同步待支付订单，超时后状态改为EXPIRE')
@pytest.mark.order
@pytest.mark.skip(reason='订单超时自动化暂停')
def test_sync_order_expire():
    '''
    同步订单信息，输入所有参数
    :return:
    '''
    ex = order.f.md5()
    aid = 'qq995939534'
    category = '110'
    service = 'MUSIC'
    sp = 'KUWO'
    origin = 'SOP1'
    business_state = 'SUCCESS'
    business_state_desc = order.f.sentence()
    title = 'sergio test order'
    status = 'WAITING_PAY'
    amount = 1.00
    discount_amount = 0.99
    actual_amount = 0.01
    vin = order.random_vin()
    info = {'info':'abcd'}
    business_info = {'business':'music'}
    coupon_id = '123456'
    coupon_amount = 0.01
    order.sync_order(ex,origin,aid,category,serviceId=service,spId=sp,businessState=business_state,businessStateDesc=business_state_desc,
                 title=title,orderStatus=status,orderCategory=category,orderType='COMMODITY',amount=amount,discountAmount=discount_amount,
                 payAmount=actual_amount,vin=vin,vehModelCode='川A88888',info=info,businessInfo=business_info,couponId=coupon_id,
                 couponAmount=coupon_amount,timeout=1,goodsId='123456',)
    sql = order.do_mysql_select('select * from `order` where ex_order_no="{}" and origin="{}"'.format(ex,origin),'fawvw_order')
    assert len(sql) == 1
    time.sleep(70)
    assert sql[0]['order_status'] == 'EXPIRE'

@allure.suite('order')
@allure.title('同步预约单')
@pytest.mark.order
@pytest.mark.skip(reason='预约单自动化暂停')
def test_sync_order_reservation():
    '''
    测试同步订单为预约单轮询检查订单状态功能

    '''
    ex = order.f.pyint()
    aid = '123456'
    category = '102'
    status = 'INIT'
    service = '111'

    res = order.sync_order(ex, 'VPA', aid, category, orderType='RESERVATION', checkFlag=True, orderStatus=status,
                       serviceId=service, spId=order.f.pyint())

    order_no = res['data']
    time.sleep(15.0)
    sql_res = order.do_mysql_select('select * from `order` where order_no="{}"'.format(order_no), 'fawvw_order')
    try:
        assert len(sql_res) == 1
        assert sql_res
        assert sql_res[0]['order_status'] == 'FINISH'
        assert sql_res[0]['check_flag'] == '0'
    finally:
        # pass
        order.do_mysql_exec('delete from `order` where order_no="{}"'.format(order_no), 'fawvw_order')


@allure.suite('order')
@allure.title('更新订单')
@pytest.mark.order
def test_update_order():
    '''
    测试更新订单，更新订单状态,业务信息
    '''
    ex = 'test001'
    aid = '123456'
    category = '102'
    origin = 'EP'
    res = order.sync_order(ex, origin, aid, category)
    order_no = res['data']
    business_info = {'name': 'sergio', 'age': '27', 'weight': '145', 'height': '174'}
    order.update_order(order_no=order_no, aid=aid, orderStatus='INIT', businessInfo=business_info)
    sql_res = order.do_mysql_select(
        'select order_status,detail from `order` o,order_detail d where o.order_no=d.order_no and o.order_no ="{}"'.format(order_no), 'fawvw_order')

    try:
        assert sql_res[0]['order_status'] == 'INIT'
        sql_res_detail = json.loads(sql_res[0]['detail'])
        assert sql_res_detail['age'] == business_info['age']
        assert sql_res_detail['name'] == business_info['name']
        assert sql_res_detail['weight'] == business_info['weight']
        assert sql_res_detail['height'] == business_info['height']
    finally:
        order.do_mysql_exec('delete from `order` where order_no="{}"'.format(order_no), 'fawvw_order')
        order.do_mysql_exec('delete from order_detail where order_no="{}"'.format(order_no), 'fawvw_order')


@allure.suite('order')
@allure.title('删除订单')
@pytest.mark.order
def test_del_order_01():
    '''
    测试删除订单，订单状态为WAITING_PAY，不能删除
    '''
    order_info = order.do_mysql_select('select * from `order` where order_status="WAITING_PAY" and del_flag=0', 'fawvw_order')
    order_info = random.choice(order_info)
    no = order_info['order_no']
    aid = order_info['aid']
    res = order.del_order(no, aid)
    assert res['errorMessage'] == '订单状态不满足条件'


@allure.suite('order')
@allure.title('删除订单')
@pytest.mark.order
def test_del_order_02():
    '''
    测试删除订单，del_flag=1的订单不能删除
    '''
    order_info = order.do_mysql_select('select * from `order` where del_flag=1', 'fawvw_order')
    order_info = random.choice(order_info)
    no = order_info['order_no']
    aid = order_info['aid']
    res = order.del_order(no, aid)
    assert res['errorMessage'] == '订单不存在'


@allure.suite('order')
@allure.title('测试消费kafka消息更改订单状态')
@pytest.mark.order
@pytest.mark.parametrize('d',[('UPDATE_BUSINESS_STATUS','1002','已完成'),('UPDATE_BUSINESS_STATUS','sergio test','sergio test desc'),
                              ('RIGHTS_OPEN',None,None),('CALLBACK','1002','已完成'),('UPDATE_BUSINESS_STATUS','1002',None),
                              ('UPDATE_BUSINESS_STATUS',None,'已完成'),('CREATION',None,None)],
                         ids=['业务改变','业务改变2','权益开通','错误的event','不填业务状态描述','不填业务状态','创建订单'])
def test_rights_open_kafka(d):
    '''
    测试消费kafka消息
    '''
    order_no = order.add_order()
    order.business_kafka(order_no,event_type=d[0],business_state=d[1],business_state_desc=d[2])
    time.sleep(2.0)
    print('暂停两秒消费kafka消息')
    sql_res = order.do_mysql_select('select * from `order` where order_no="{}"'.format(order_no),'fawvw_order')
    try:
        if d[0] == 'RIGHTS_OPEN':
            assert sql_res[0]['order_status'] == 'FINISH'
        elif d[0] == 'UPDATE_BUSINESS_STATUS':
            if d[1]:
                assert sql_res[0]['business_status'] == d[1]
            if d[2]:
                assert sql_res[0]['business_status_desc'] == d[2]
        elif d[0] == 'CREATION':
            assert len(sql_res) == 1
        else:
            return
    finally:
        pass
        # order.do_mysql_exec(
        #     'delete from order_detail where order_id=(select id from `order` where order_no="{}")'.format(order_no),
        #     'fawvw_order')
        # order.do_mysql_exec('delete from `order` where order_no="{}"'.format(order_no),'fawvw_order')

