import pytest
import allure
from flow.flow_api import Flow


flow = Flow()

@allure.suite('flow')
@allure.title('获取流量详情测试用例')
@pytest.mark.flow
@pytest.mark.parametrize('id',['253','254','255','85'])
def test_flow_detail(id):
    res = flow.bm_get_flow_detail(id)
    assert res['code'] == 0
    sql = flow.do_mysql_select('SELECT g.*,f.description,c.goodsStatus from GOODS g,'
                               'FLOW_ATTRIBUTE f,GOODS_CONTROL c where 1=1 and g.id = c.goodsId and '
                               'g.goodsCodes=f.goodsCodes and c.goodsStatus="ALREADY_SHELVES" and g.id={}'.format(id),'fawvw_flow','SOP2')
    assert res['data']['goodsName'] == sql[0]['goodsName']
    assert res['data']['descripiton'] == sql[0]['description']
    assert res['data']['termsOfserviceUrl'] == sql[0]['goodsUrl']
    assert res['data']['price'] == sql[0]['goodsPrice']
