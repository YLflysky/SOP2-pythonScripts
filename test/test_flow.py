import pytest
import allure
import random
import sys
from flow.flow_api import Flow
from order.payment import Payment
from box.lk_logger import lk

pay = Payment()
flow = Flow()


@allure.suite('flow')
@allure.title('BM车机端获取流量详情测试用例')
@pytest.mark.flow
@pytest.mark.parametrize('id',['266','254','255','85'])
def test_bm_flow_detail(id):
    res = flow.bm_get_flow_detail(id)
    assert res['code'] == 0
    sql = flow.do_mysql_select('SELECT g.*,f.description,c.goodsStatus from GOODS g,'
                               'FLOW_ATTRIBUTE f,GOODS_CONTROL c where 1=1 and g.id = c.goodsId and '
                               'g.goodsCodes=f.goodsCodes and c.goodsStatus="ALREADY_SHELVES" and g.id={}'.format(id),'fawvw_flow','SOP2')
    assert res['data']['goodsName'] == sql[0]['goodsName']
    assert res['data']['descripiton'] == sql[0]['description']
    assert res['data']['termsOfserviceUrl'] == sql[0]['goodsUrl']
    assert res['data']['price'] == sql[0]['goodsPrice']


@allure.suite('flow')
@allure.title('底层获取流量详情测试用例')
@pytest.mark.flow
@pytest.mark.parametrize('goods_id',['100','101','102','256','257','258']
                         ,ids=['酷我1个月VIP','酷我3个月VIP','酷我6个月VIP','在线媒体月包','在线媒体季包','Wi-Fi半年包'])
def test_flow_detail(goods_id):
    res = flow.flow_detail(goods_id)
    assert res['returnStatus'] == 'SUCCEED'
    assert res['data']['goodsControlStatus'] == 'ALREADY_SHELVES'
    assert res['data']['goodsName']


@allure.suite('flow')
@allure.title('BM车机端获取流量详情')
@pytest.mark.flow
@pytest.mark.parametrize('goods',[None,flow.f.pyint(),'261','246'],
                         ids=['不输入商品编号','不存在的编号','商品已下架','商品未上架'])
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
@pytest.mark.parametrize('param',[(flow.f.pyint(),1,1,1,'ALI_PAY','OPEN'),(flow.f.pyint(),2,2,2,'WECHAT_PAY','CLOSE'),
                                  (flow.f.pyint(),2,1,1,'WECHAT_PAY','OPEN'),(flow.f.pyint(),1,2,2,'ALI_PAY','CLOSE')]
                         ,ids=['支付宝签约','微信解约','微信签约','支付宝解约'])
def test_sign_result_callback(param):
    res = flow.sign_result_callback(param[0],param[1],param[2],param[3])
    assert res['status'] == '0000_0'
    assert res['messages'][0] == '成功'


@allure.suite('flow')
@allure.title('免密签约结果回调')
@pytest.mark.flow
@pytest.mark.parametrize('d',[('221',1,1,2),('221',1,2,1),('221',3,1,1)],
                         ids=['状态为未签约，通知类型为签约','状态为已签约，通知类型为解约','支付渠道错误'])
def test_sign_result_callback_wrong(d):
    '''
    测试免密签约回调异常情况
    :return:
    '''
    res = flow.sign_result_callback(d[0],d[1],d[2],d[3])
    assert res['status'] == '0000_1'
    assert res['messages'][0] == '失败'


@allure.suite('flow')
@allure.title('免密支付结果回调')
@pytest.mark.flow
def test_pay_result_callback():
    '''
    测试支付成功回调
    :return:
    '''
    aid = 'qq995939534'
    order_msg = flow.bm_create_flow_order(goods_id='5b7cf4f565914cab86cf71ef9ca34e99', aid=aid, vin='LFVSOP2TEST000353',
                              quantity=1)
    order_no = order_msg['data']['orderNo']
    # 根据流量订单支付
    res = pay.get_qr_code(aid,order_no,channel='ALI_PAY')
    assert res['returnStatus'] == 'SUCCEED'
    # 获取支付payNo
    pay_no = pay.do_mysql_select('select pay_no from pay_order where order_no="{}" and is_effective=1'.format(order_no),'fawvw_pay')
    pay_no = pay_no[0]['pay_no']
    success_attr = {'thirdPartyPaymentSerial': 'qq995939534', 'payChannel': 'ALI_PAY',
                    'paidTime': flow.time_delta(formatted='%Y%m%d%H%M%S')}
    res = flow.common_callback(id=flow.f.pyint(),category=1,status='1000_00',origin_id=pay_no,additionalAttrs=success_attr)
    assert res['status'] == '0000_0'
    assert res['messages'][0] == '成功'
    sql = flow.do_mysql_select('select order_status from `order` where order_no="{}"'.format(order_no),'fawvw_order')
    assert sql[0]['order_status'] == 'PAY_SUCCESS'
    sql = flow.do_mysql_select('select pay_status from pay_order where pay_no="{}"'.format(pay_no),'fawvw_pay')
    assert sql[0]['pay_status'] == 'SUCCESS'