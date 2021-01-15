import pytest
from calendar_file.canlendar_api import Calendar
import allure
import random
from box.lk_logger import lk
from box.base import Base

name = '13353116624'
password = '000000'
aid = '9353497'

base = Base(tenant='BM')


event_id = random.randint(10000, 100000)
event = {'localEventId':event_id , 'cudStatus': 'C','rrule':'Only Once',
                     'eventStartTime': base.get_time_stamp(days=-1), 'eventEndTime': base.get_time_stamp(days=1)}

@allure.suite('calendar')
@allure.title('测试账号的项目类型是否正确')
@pytest.mark.app_calendar
def test_tenant():
    sop1_c = Calendar('SOP1', name, password, 'LFVSOP2TESTLY0010', aid)
    assert sop1_c.get_tenant_by_vin() == 'SOP1'
    lk.prt('check SOP1 tenant success')

    w37_c = Calendar('37W', name, password, 'LFVSOP2TESTLY0011', aid)
    assert w37_c.get_tenant_by_vin() == '37W'
    lk.prt('check 37W tenant success')

def assert_results():
    '''
    查询数据库看是否同步成功
    :return:
    '''
    sql_res = base.do_mysql_select('SELECT * from calendar_event where uid="{}" and local_event_id="{}"'.format(aid,event_id),'fawvw_calendar')
    try:
        assert len(sql_res) == 1
    finally:
        base.do_mysql_exec('delete from calendar_event where uid="{}" and local_event_id="{}"'.format(aid,event_id),'fawvw_calendar')



@allure.suite('calendar')
@allure.title('测试SOP2BM车型通过APP同步日历事件')
@pytest.mark.app_calendar
def test_sop2_bm_app_sync_event():
    bm_c = Calendar('BM', name, password, 'LFVSOP2TESTLY0003', aid)
    assert bm_c.get_tenant_by_vin() == 'SOP2BM'
    lk.prt('check SOP2BM tenant success')
    res = bm_c.mobile_sync(current_time=None,events=[event])
    assert_results()



@allure.suite('calendar')
@allure.title('测试SOP2MA车型通过APP同步日历事件')
@pytest.mark.app_calendar
def test_sop2_ma_app_sync_event():
    ma_c = Calendar('MA', name, password, 'LFVSOP2TESTLY0002', aid)
    assert ma_c.get_tenant_by_vin() == 'SOP2MA'
    lk.prt('check SOP2MA tenant success')
    res = ma_c.mobile_sync(current_time=None,events=[event])
    assert_results()