import pytest
import allure
from order.bm_payment import BMPayment
from order.bm_order import BMOrder
import json
import random

order = BMOrder()
pay = BMPayment()


@pytest.mark.payment
@allure.suite('payment')
@allure.title('BM适配层获取二维码')
@pytest.mark.parametrize('code',['11100','12100'],ids=['获取支付宝二维码','获取微信二维码'])
def test_bm_get_qr_code(code):
    '''
    测试BM获取支付二维码
    '''
    # 同步一条音乐订单，用于获取支付二维码
    ex_order_no = order.f.pyint()
    goods_id = order.f.pyint()
    vin = order.random_vin()
    ext_info = order.f.pydict(4, True, value_types=str)
    discount_amount = '10000'
    order_amount = order.f.pyint(10086, 100000)
    category = '111'
    sp_id = 'KUWO'
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
        res = order.sync_bm_order(ex_order_no, data)
        order_no = res['data']
        # 更新订单来源为SOP1
        order.do_mysql_exec('update `order` set origin="SOP1",actual_pay_amount=0.01 where order_no="{}"'.format(order_no),'fawvw_order')

        # 获取二维码
        res = pay.get_qr_code(vin=vin,aid=user_id,order_no=order_no,pay_type=code,category=category)

        assert res['data']['getPayQrCodeResp']['qrByteData']
    finally:
        pass
        # order.do_mysql_exec('delete from order_detail where order_id =(select id from `order` where order_no="{}")'.format(order_no),'fawvw_order')
        # order.do_mysql_exec('delete from `order` where order_no="{}" and aid="{}"'.format(order_no,user_id), 'fawvw_order')
        # pay.do_mysql_exec('delete from order_id_relation where order_no="{}"'.format(order_no),'fawvw_pay')
        # pay.do_mysql_exec('delete from pay_order where order_no="{}"'.format(order_no),'fawvw_pay')

@pytest.mark.payment
@allure.suite('payment')
@allure.title('BM适配层获取二维码')
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


@pytest.mark.parametrize('param',[('9642113','11112222333','zh-CN','11101','中文1'),
                                  ('9642113','20200904132809784139264','en-US','12101','DDWQDQW'),
                                  ('4614907','20201012103736463180224','zh-CN','11101','加油')],
                         ids=['获取支付宝支付中文协议','获取微信支付英文协议','获取加油支付宝协议'])
@pytest.mark.payment
@allure.suite('payment')
@allure.title('BM适配层获取支付协议')
def test_bm_pay_agreement(param):
    '''
    测试获取支付协议
    '''
    res = pay.get_pay_agreement(param[0],param[1],param[3],param[2])
    assert res['data']['title'] == param[-1]
    assert res['data']['content']


@pytest.mark.parametrize('param',[('zh-CN','服务条款及免责声明'),
                                  ('en-US','Terms of Service and Disclaimer')],
                         ids=['获取中文默认支付协议','获取英文默认支付协议'])
@pytest.mark.payment
@allure.suite('payment')
@allure.title('BM适配层获取支付协议')
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
@allure.title('BM适配层获取支付协议')
def test_bm_pay_agreement_wrong(param):
    '''
    测试获取支付协议异常情况
    '''
    res = pay.get_pay_agreement(param[0],param[1],param[2],param[3])
    assert 'error' in json.dumps(res)


@pytest.mark.payment
@allure.suite('payment')
@allure.title('BM适配层获取支付结果')
@pytest.mark.parametrize('data',[('20200907105829249819204','32432','102','100'),
                                 ('20201109132011110380928','221','105','100'),
                                 ('ftb20201127151324000753664','qq995939534','111','102'),
                                 ('ftb20201127113931728753664','qq995939534','111','101')],
                         ids=['获取正在支付的支付结果','获取音乐订单支付','获取支付失败结果','获取流量订单支付结果'])
def test_bm_pay_result(data):
    '''
    测试BM适配层获取支付结果
    '''
    vin = 'LFVSOP2TEST000353'
    res = pay.get_pay_result(vin=vin,order_no=data[0],aid=data[1],category=data[2],roll_number=1)
    sql = pay.do_mysql_select('select buyer_account from pay_order where order_no="{}"'.format(data[0]),'fawvw_pay')
    assert res['data']['payResultStatus'] == data[-1]

    assert res['data']['buyerAccount'] == sql[0]['buyer_account']


@pytest.mark.payment
@allure.suite('payment')
@allure.title('BM适配层获取支付结果')
@pytest.mark.parametrize('data',[('111','orderNo0002','9642113','102',1),
                                 ('kk123','20201027135001071204800','ramos','102',1),
                                 ('','20201027113016328225280','1603769416000','102',1)],
                         ids=['输入的订单没有支付结果','输入不存在的订单','不输入vin'])
def test_bm_pay_result_wrong(data):
    '''
    测试BM适配层获取支付结果异常情况
    '''
    res = pay.get_pay_result(data[0],data[1],data[2],data[3],data[4])
    assert 'error' in json.dumps(res)


@allure.suite('payment')
@allure.title('BM车机端获取支付方式')
@pytest.mark.payment
def test_bm_pay_channel_flow():
    '''
    测试获取流量订单支付方式，支持免密支付
    :return:
    '''
    vin = 'SO8OY5T6JXM7B76O6'
    aid = '122'
    data = pay.do_mysql_select('select * from pay_order where service_id="FLOW" and sp_id="CMCC" and aid="{}"'.format(aid),'fawvw_pay')
    data = random.choice(data)

    order_no = data['order_no']
    res = pay.get_pay_channel(vin,aid,order_no,category=111)
    for l in res['data']['gatewayList']:
        assert l['isSupportNoPasswordPay'] == '1'


@allure.suite('payment')
@allure.title('BM车机端获取支付方式')
@pytest.mark.payment
def test_bm_pay_channel():
    aid = '122'
    no = 'ftb20201204113739602753664'
    res = pay.get_pay_channel(pay.random_vin(),aid,no,category='111')
    assert res['data']['preferGatewayCode'] in ('11','12')
    assert res['data']['gatewayList']