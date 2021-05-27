from .conftest import s,lk
import pytest
import allure


@allure.suite('ftb3.0对账功能')
@allure.title('对账单列表查询>>根据spId查询')
@pytest.mark.statement
@pytest.mark.parametrize('sp',[('KUWO','JDO','FLEETIN')])
def test_statement_list_01(sp):
    res = s.statement_list(third_name=sp[0])
    data = res['data']
    assert res['totalCount'] == len(data)
    if len(data) != 0:
        assert data[0]['statementNo']
        assert data[0]['statementDate']
        assert data[0]['statementPeriodType']
        assert data[0]['thirdName'] == sp[0]
        assert data[0]['brand']
        assert data[0]['platformRecordSum']
        assert data[0]['platformMoneyAmount']
        assert data[0]['thirdRecordSum']
        assert data[0]['thirdMoneyAmount']
        assert data[0]['settleMoneyAmount']
        assert data[0]['settleRecordSum']
        assert data[0]['platformProportion']
        assert data[0]['platformShare']
        assert data[0]['thirdShare']
        assert data[0]['balanceRecordSum']
        assert data[0]['balanceMoneyAmount']
        assert data[0]['diffRecordSum']
        assert data[0]['statementStatus']


@allure.suite('ftb3.0对账功能')
@allure.title('对账单列表查询>>statementStatus筛选')
@pytest.mark.statement
def test_statement_list_02():
    res = s.statement_list(third_name='KUWO',statementStatus='CHECKED')
    sql_res = s.do_mysql_select('select count(1) as t from statement where third_name="KUWO" and statement_status="CHECKED"',
                                'ftb_bill',host='FTB3')
    assert res['totalCount'] == sql_res[0]['t']


@allure.suite('ftb3.0对账功能')
@allure.title('对账单列表查询>>beginTime,endTime筛选')
@pytest.mark.statement
def test_statement_list_03():
    begin = '2021-04-01 00:00:00'
    end = '2021-05-01 00:00:00'
    res = s.statement_list(third_name='FLEETIN',beginTime=begin,endTime=end)
    sql_res = s.do_mysql_select('select count(1) as t from statement where third_name="FLEETIN" and  statement_date between "{}" and "{}"'.format(begin,end),
                                'ftb_bill',host='FTB3')
    assert res['totalCount'] == sql_res[0]['t']


@allure.suite('ftb3.0对账功能')
@allure.title('明细列表查询>>输入对账单号查询')
@pytest.mark.statement
def test_item_list_01():
    res = s.item_list(s_no='112')
    if res['totalCount'] != 0:
        res = res['data'][0]
        assert res['id']
        assert res['statementCheckNo']
        # assert res['platformRecordNo']
        # assert res['platformRecordMoney']
        # assert res['platformRecordExtend']
        # assert res['thirdRecordNo']
        # assert res['thirdRecordMoney']
        # assert res['thirdRecordExtend']
        assert res['status']

@allure.suite('ftb3.0对账功能')
@allure.title('对账单列表查询>>beginTime,endTime筛选')
@pytest.mark.statement
@pytest.mark.parametrize('d_type',['BALANCE','MORE','LESS','DIFF'])
def test_item_list_02(d_type):

    res = s.item_list(s_no='112',diffType=d_type)
    sql_res = s.do_mysql_select('select count(1) as t from statement_item where statement_no="112" and  diff_type="{}"'.format(d_type),
                                'ftb_bill',host='FTB3')
    assert res['totalCount'] == sql_res[0]['t']


@allure.suite('ftb3.0对账功能')
@allure.title('对账功能全周期测试')
@pytest.mark.statement
@pytest.mark.parametrize('s_type',['PAY_STATEMENT','ORDER_STATEMENT'])
def test_statement_lifecycle(s_type):

    res = s.generate_statement(cp='JD_OPEN',s_time='2020-10-24 14:00:00',percent_platform=25.5,s_p_type='MONTH',s_type=s_type)
    s_no = res['data']['statementNo']
    items = s.item_list(s_no)
    for i in items['data']:
        if not i['checkTime']:
            s.item_check(s_no,s_c_no=i['statementCheckNo'],s_m_amount=i['platformRecordMoney'],s_r_no=1,remarks=s.f.sentence())
            lk.prt('{}明细确认成功！'.format(i['statementCheckNo']))
    s.confirm_statement(s_no)
    lk.prt('确认账单成功:{}'.format(s_no))
    s.upload_statement(s_no)
    with open('../data/对账单.pdf','r') as obj:
        obj.read()