import pytest
import allure
from order.bm_payment import BMPayment
from order.bm_order import BMOrder
import os
import json

os.environ['ENV'] = 'UAT'
os.environ['GATE'] = 'false'

order = BMOrder()
pay = BMPayment()


@pytest.mark.payment
@allure.suite('payment')
@allure.story('bm adapter')
@pytest.mark.parametrize('code',['11101','12101'])
def test_bm_get_qr_code(code):
    '''
    测试BM获取支付二维码
    '''
    # 同步一条订单，用于获取支付二位码
    id = order.f.pyint()
    goods_id = order.f.pyint()
    vin = order.f.pyint()
    ext_info = order.f.pydict(4, True, value_types=str)
    discount_amount = '10000'
    order_amount = order.f.pyint(10086, 100000)
    category = '111'
    sp_id = 'CLOUD MUSIC'
    service_id = 'MUSIC'
    title = order.f.sentence()
    user_id = '221'
    status = 'FINISH'
    status_desc = 'jojo'
    data = {'vin': vin, 'brand': 'AUDI', 'businessExtInfo': ext_info, 'discountAmount': discount_amount,
            'orderAmount': order_amount,
            'orderCategory': category, 'spId': sp_id, 'serviceId': service_id, 'title': title, 'userId': user_id,
            'serviceOrderState': status, 'serviceOrderStateDesc': status_desc,'goodsId':goods_id}
    try:
        res = order.sync_bm_order(id, data)
        order_no = res['data']
        # 更新订单来源为SOP1
        order.do_mysql_exec('update `order` set origin="SOP1",actual_pay_amount=0.01 where order_no="{}"'.format(order_no),'order')

        # 获取二维码
        res = pay.get_qr_code(vin=vin,aid=user_id,order_no=order_no,pay_type=code,category=category)

        assert res['data']['qrCode']
    finally:
        order.do_mysql_exec('delete from order_detail where order_id =(select id from `order` where order_no="{}")'.format(order_no),'order')
        order.do_mysql_exec('delete from `order` where order_no="{}" and aid="{}"'.format(order_no,user_id), 'order')
        pay.do_mysql_exec('delete from order_id_relation where order_no="{}"'.format(order_no),'mosc_pay')
        pay.do_mysql_exec('delete from pay_order where order_no="{}"'.format(order_no),'mosc_pay')

@pytest.mark.payment
@allure.suite('payment')
@allure.story('bm adapter')
@pytest.mark.parametrize('param',[('1','001','orderNo0001','121010','100'),
                                  ('1','001','orderNo000','12101','100'),
                                  ('','001','orderNo0001','11101','100'),
                                  ('1','dwqdwq','orderNo0001','11101','100'),
                                  ('1','001',None,'11101','100'),
                                  ('1','001','orderNo0001',None,'100')],
                         ids=['支付类型错误','通过aid+orderNo找不到订单','不输入vin','不输入aid','不输入orderNo','不输入agreementCode'])
def test_bm_get_qr_code_wrong(param):
    '''
    测试获取支付二维码异常情况
    '''
    res = pay.get_qr_code(param[0],param[1],param[2],param[3],param[4])
    assert 'error' in json.dumps(res)


@pytest.mark.parametrize('param',[('9642113','11112222333','zh-CN','11101'),
                                  ('9642113','M202007160901278277176514','en-US','12101'),
                                  ('4614907','20201012103736463180224','zh-CN','11101')],
                         ids=['获取支付宝支付中文协议','获取微信支付英文协议','获取加油支付宝协议'])
@pytest.mark.payment
@allure.suite('payment')
def test_bm_pay_agreement(param):
    '''
    测试获取支付协议
    '''
    res = pay.get_pay_agreement(param[0],param[1],param[3],param[2])
    assert res['data']['title']
    assert res['data']['content']


@pytest.mark.parametrize('param',[('zh-CN','服务条款及免责声明'),
                                  ('en-US','Terms of Service and Disclaimer')],ids=['获取中文默认支付协议','获取英文默认支付协议'])
@pytest.mark.payment
@allure.suite('payment')
def test_bm_pay_agreement_default(param):
    '''
    测试获取默认支付协议
    '''
    res = pay.get_pay_agreement('221','20201030062521612266240','12101',param[0])
    assert param[1] in res['data']['title']


@pytest.mark.parametrize('param',[(None,'81676918110561974562','11101','zh-CN',),
                                  ('221','','11101','zh-CN'),
                                  ('221','81676918110561974562','111010','zh-CN'),
                                  ('221','81676918110561974562','11101','zh-CN1'),
                                  ('221','qwer','11101','zh-CN')],
                         ids=['不输入aid','不输入orderNo','输入code不支持','输入语言错误','输入订单不存在'])
@pytest.mark.payment
@allure.suite('payment')
def test_bm_pay_agreement_wrong(param):
    '''
    测试获取支付协议异常情况
    '''
    res = pay.get_pay_agreement(param[0],param[1],param[2],param[3])
    assert 'error' in json.dumps(res)


@pytest.mark.payment
@allure.suite('payment')
@pytest.mark.parametrize('data',[('111','orderNo0001','9642113','102',1),
                                 ('111','20201027135001071204800','33','102',1),
                                 ('111','1235','1234','102',1),
                                 ('111','20201027113016328225280','1603769416000','102',1)],
                         ids=['获取正在支付的支付结果','获取支付成功结果','获取支付失败结果','支付成功'])
def test_bm_pay_result(data):
    '''
    测试BM适配层获取支付结果
    '''
    res = pay.get_pay_result(data[0],data[1],data[2],data[3],data[4])
    sql = pay.do_mysql_select('select pay_status,buyer_account from pay_order where order_no="{}" order by pay_time desc limit 1'.format(data[1]),'mosc_pay')
    if sql[0]['pay_status'] == 'PROCESSING':
        assert res['data']['payResultStatus'] == '100'
    elif sql[0]['pay_status'] == 'SUCCESS':
        assert res['data']['payResultStatus'] == '101'

    elif sql[0]['pay_status'] == 'FAILED':
        assert res['data']['payResultStatus'] == '102'

    assert res['data']['buyerAccount'] == sql[0]['buyer_account']


@pytest.mark.payment
@allure.suite('payment')
@pytest.mark.parametrize('data',[('111','orderNo0002','9642113','102',1),
                                 ('111','20201027135001071204800','33','',1),
                                 ('111','1235','1234','102',''),
                                 ('','20201027113016328225280','1603769416000','102',1)],
                         ids=['输入的订单没有支付结果','不输入category','不输入rollNumber','不输入vin'])
def test_bm_pay_result_wrong(data):
    '''
    测试BM适配层获取支付结果异常情况
    '''
    res = pay.get_pay_result(data[0],data[1],data[2],data[3],data[4])
    assert 'error' in json.dumps(res)