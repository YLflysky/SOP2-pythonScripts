import pytest
import allure
from flow.flow_api import Flow


flow = Flow()
# 测试用例数据
goods = ['266','254','255','85']

@allure.suite('flow')
@allure.title('BM车机端获取流量详情测试用例')
@pytest.mark.flow
@pytest.mark.parametrize('id',goods)
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
@pytest.mark.parametrize('id',goods)
def test_flow_detail(id):
    res = flow.flow_detail(id)
    assert res['returnStatus'] == 'SUCCEED'

    assert res['data']['goodsControlStatus'] == 'ALREADY_SHELVES'


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
    assert res['messages'] == '成功'
    sql = flow.do_mysql_select('select * from contract_sign where aid={}'.format(param[0]),'fawvw_pay')
    assert len(sql) == 1
    assert sql[0]['pay_channel'] == param[-2]
    assert sql[0]['sign_status'] == param[-1]


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
