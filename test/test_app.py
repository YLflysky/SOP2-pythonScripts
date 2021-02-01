import pytest
import allure
import random
from box.lk_logger import lk
from app.app_api import App

name = '13353116624'
password = '000000'
aid = '9353497'

app = App(name,password,aid=aid)


event_id = random.randint(10000, 100000)
event = {'localEventId':event_id , 'cudStatus': 'C','rrule':'Only Once',
                     'eventStartTime': app.get_time_stamp(days=-1), 'eventEndTime': app.get_time_stamp(days=1)}


def assert_results():
    '''
    查询数据库看是否同步成功
    :return:
    '''
    sql_res = app.do_mysql_select('SELECT * from calendar_event where uid="{}" and local_event_id="{}"'.format(aid,event_id),'fawvw_calendar')
    try:
        assert len(sql_res) == 1
    finally:
        app.do_mysql_exec('delete from calendar_event where uid="{}" and local_event_id="{}"'.format(aid,event_id),'fawvw_calendar')

vins = [('LFVSOP2TESTLY0003','SOP2BM'),
        ('LFVSOP2TESTLY0002','SOP2MA'),
        ('LFVSOP2TESTLY0010','37W'),
        ('LFVSOP2TESTLY0011','SOP1')]


@allure.suite('app')
@allure.title('测试传入vin判断车型，然后通过APP同步日历事件')
@pytest.mark.app
@pytest.mark.parametrize('vin',vins)
def test_app_sync_event(vin):
    lk.prt(vin)
    vin_code = vin[0]
    tenant = vin[1]
    assert app.get_tenant_by_vin(vin_code) == tenant
    lk.prt('check {} tenant success'.format(tenant))
    res = app.calendar_mobile_sync(current_time=None,events=[event],vin=vin_code)
    if tenant in ('SOP2BM','SOP2MA'):
        assert_results()


@allure.suite('app')
@allure.title('测试传入vin判断车型，然后查询所有日历事件')
@pytest.mark.app
@pytest.mark.parametrize('vin',vins[:2])
def test_app_calendar_find_all(vin):
    app.calendar_mobile_find_all(vin=vin[0])




