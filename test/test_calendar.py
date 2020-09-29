import pytest
from calendar_file.canlendar_api import Calendar
import os
import allure

os.environ['GATE'] = 'false'
os.environ['ENV'] = 'LOCAL'
c = Calendar()

@pytest.fixture()
def del_event(**kwargs):
    yield
    c.del_event(**kwargs)

def log_time(func):
    def make_decorater(*args,**kwargs):
        print('现在开始装饰')
        func(*args,**kwargs)
        print('现在结束装饰')
    return make_decorater

@allure.suite('calendar')
@allure.story('add event')
@pytest.mark.calendar
@log_time
def test_add_event_01():
    '''
    输入全部必填项，添加日历事件
    '''
    start_time = c.get_time_stamp(days=10)
    end_time = c.get_time_stamp(days=11)

    calendar_id = c.add_event(start_time, end_time)['data']['id']
    sql_res = c.do_mysql_select(
        'select uid,origin,start_time,end_time from calendar_event where id={}'.format(calendar_id),
        db='fawvw_golf_calendar')
    try:
        assert sql_res[0]['uid'] == '9350195'
        assert sql_res[0]['origin'] == 'HU'
        assert sql_res[0]['start_time'] == c.stamp_to_str(start_time)
        assert sql_res[0]['end_time'] == c.stamp_to_str(end_time)
    finally:
        c.del_event(event_id=calendar_id)

@allure.suite('calendar')
@allure.story('add event')
@pytest.mark.calendar
def test_add_event_02():
    '''
    输入全部必填项，输入全部选填项
    '''
    start_time = c.get_time_stamp(days=10)
    end_time = c.get_time_stamp(days=11)
    event_name = c.f.word()
    address = c.f.address()
    longitude = '123.00'
    latitude = '23.00'
    remarks = c.f.sentence()
    allday = True
    create_time = c.get_time_stamp()
    duration = '123'
    local_event_id = c.f.pyint()

    calendar_id = c.add_event(start_time, end_time,
                              localEventId=local_event_id,
                              eventName=event_name,
                              address=address,
                              longitude=longitude,latitude=latitude,remarks=remarks,
                              duration=duration,createTime=create_time,allday=allday)['data']['id']
    sql_res = c.do_mysql_select(
        'select * from calendar_event where id={}'.format(calendar_id),
        db='fawvw_golf_calendar')
    try:
        assert sql_res[0]['uid'] == '9350195'
        assert sql_res[0]['origin'] == 'HU'
        assert sql_res[0]['start_time'] == c.stamp_to_str(start_time)
        assert sql_res[0]['end_time'] == c.stamp_to_str(end_time)
        assert sql_res[0]['address'] == address
        assert sql_res[0]['local_event_id'] == str(local_event_id)
        assert sql_res[0]['remarks'] == remarks
    finally:
        c.del_event(event_id=calendar_id)

@allure.suite('calendar')
@allure.story('add event')
@pytest.mark.calendar
def test_add_event_03():
    '''
    输入开始时间在结束时间之后，报错
    '''
    s = c.get_time_stamp(days=2)
    e = c.get_time_stamp(days=1)
    code,body = c.add_event(s,e)
    assert body['statusMessage'] == 'wrong date range'

@allure.suite('calendar')
@allure.story('update event')
@pytest.mark.calendar
def test_update_event():
    s = c.get_time_stamp()
    e = c.get_time_stamp(days=1)
    id = c.add_event(s,e)['data']['id']
    c.update_event(event_id=id,longitude='1.00',latitude='1.00',s=s,e=e,address='铜梁区')
    sql_res = c.do_mysql_select('select * from calendar_event where id={}'.format(id),'fawvw_golf_calendar')
    try:
        assert float(sql_res[0]['longitude'])==1.00
        assert float(sql_res[0]['latitude'])==1.00
        assert sql_res[0]['address']=='铜梁区'
    finally:
        c.del_event(id)



