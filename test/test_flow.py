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
