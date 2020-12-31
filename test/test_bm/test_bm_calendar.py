import pytest
from calendar_file.canlendar_api import Calendar
import allure
import random

c = Calendar('BM')


@pytest.fixture()
def del_event(**kwargs):
    yield
    c.del_event(**kwargs)


def log_time(func):
    def make_decorater(*args, **kwargs):
        print('现在开始装饰')
        func(*args, **kwargs)
        print('现在结束装饰')

    return make_decorater


@allure.suite('calendar')
@allure.title('BM车机端新增用户日历事件')
@pytest.mark.calendar
def test_add_event_01():
    '''
    输入全部必填项，添加日历事件
    '''
    start_time = c.get_time_stamp(days=10)
    end_time = c.get_time_stamp(days=11)

    calendar_id = c.add_event(start_time, end_time)['data']['id']
    sql_res = c.do_mysql_select(
        'select uid,origin,start_time,end_time from calendar_event where id={}'.format(calendar_id),
        db='fawvw_calendar')
    try:
        assert sql_res[0]['uid'] == '9350195'
        assert sql_res[0]['origin'] == 'HU'
        assert sql_res[0]['start_time'] == c.stamp_to_str(start_time)
        assert sql_res[0]['end_time'] == c.stamp_to_str(end_time)
    finally:
        c.del_event(event_id=calendar_id)


@allure.suite('calendar')
@allure.title('BM车机端新增用户日历事件》》输入全部必填项')
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
                              longitude=longitude, latitude=latitude, remarks=remarks,
                              duration=duration, createTime=create_time, allday=allday)['data']['id']
    sql_res = c.do_mysql_select(
        'select * from calendar_event where id={}'.format(calendar_id),
        db='fawvw_calendar')
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
@allure.title('BM车机端新增用户日历事件》》异常')
@pytest.mark.calendar
def test_add_event_03():
    '''
    输入开始时间在结束时间之后，报错
    '''
    s = c.get_time_stamp(days=2)
    e = c.get_time_stamp(days=1)
    body = c.add_event(s, e)

    assert body['errorMessage'] == 'wrong date range'


@allure.suite('calendar')
@allure.title('BM车机端新增用户日历事件》》传入rrule')
@pytest.mark.calendar
def test_add_event_04():
    '''
    传入rrule
    '''
    s = c.get_time_stamp(days=-100)
    e = c.get_time_stamp(days=100)
    id = c.add_event(s, e, rrule='Only Once')['data']['id']
    sql_res = c.do_mysql_select(
        'select * from calendar_event where id={}'.format(id),
        db='fawvw_calendar')

    assert sql_res[0]['rrule'] == 'Only Once'


@allure.suite('calendar')
@allure.title('BM车机端新增用户日历事件》》传入错误的rrule')
@pytest.mark.calendar
def test_add_event_05():
    '''
    传入错误的rrule
    '''
    s = c.get_time_stamp(days=2)
    e = c.get_time_stamp(days=3)
    body = c.add_event(s, e, rrule='Only Once1')
    assert body['errorMessage'] == 'rule resolve error'


@allure.suite('calendar')
@allure.title('BM车机端更新用户日历事件')
@pytest.mark.calendar
def test_update_event():
    s = c.get_time_stamp()
    e = c.get_time_stamp(days=1)
    id = c.add_event(s, e)['data']['id']
    c.update_event(event_id=id, longitude='1.00', latitude='1.00', s=s, e=e, address='铜梁区')
    sql_res = c.do_mysql_select('select * from calendar_event where id={}'.format(id), 'fawvw_calendar')
    try:
        assert float(sql_res[0]['longitude']) == 1.00
        assert float(sql_res[0]['latitude']) == 1.00
        assert sql_res[0]['address'] == '铜梁区'
    finally:
        c.del_event(id)


@allure.suite('calendar')
@allure.title('BM车机端查询用户所有事件')
@pytest.mark.calendar
@pytest.mark.parametrize('t', [1601203105641, None])
def test_find_all(t):
    '''
    获取用户全部日历信息，输入时间
    '''
    body = c.find_all_event(update_time=t)
    assert len(body['data']['events']) > 0


@allure.suite('calendar')
@allure.title('BM车机端查询用户所有事件>>验证能查询出app同步的事件')
@pytest.mark.calendar
def test_find_all():
    '''
    获取用户全部日历信息，输入时间
    '''
    body = c.find_all_event(update_time=None)
    sql = c.do_mysql_select('select count(1) as events from calendar_event where uid ="9350195" and cud_status in ("C","U")','fawvw_calendar')
    assert len(body['data']['events']) == sql[0]['events']
    print('用户所有日历事件个数:{}'.format(sql[0]['events']))


@allure.suite('calendar')
@allure.title('BM车机端查询用户事件详情')
@pytest.mark.calendar
def test_find_detail_success():
    '''
    通过事件id成功查找单个日历事件详情
    '''
    st = c.get_time_stamp()
    et = c.get_time_stamp(seconds=10)
    id = c.add_event(st, et)['data']['id']
    body = c.find_detail(id)
    try:
        assert body['data']['id'] == id
        assert body['data']['eventStartTime'] == st
        assert body['data']['eventEndTime'] == et
    finally:
        c.del_event(id)


@allure.suite('calendar')
@allure.title('BM车机端查询用户事件详情>>异常')
@pytest.mark.calendar
@pytest.mark.parametrize('id', [123, 'abc', 1, 2, 3])
def test_find_detail_fail(id):
    '''
    查找单个日历事件详情异常情况
    '''
    body = c.find_detail(id)
    assert 'data' not in body.keys()


@allure.suite('calendar')
@allure.title('BM车机端获取用户事件列表')
@pytest.mark.calendar
@pytest.mark.parametrize('t', ['TYPE_ONE', 'TYPE_TWO', 'TYPE_THREE'])
def test_get_event_list_01(t):
    '''
    查询指定时间段时间列表,仅输入apiType
    '''
    data = {'apiType': t}
    body = c.get_event_list(data)
    assert len(body['data']['events']) > 0


@allure.suite('calendar')
@allure.title('BM车机端获取用户事件列表')
@pytest.mark.calendar
def test_get_event_list_02():
    '''
    查询指定时间段时间列表,输入Date
    '''
    data = {'apiType': 'TYPE_ONE', 'startDate': '1602210000', 'endDate': '1602291000'}
    body = c.get_event_list(data)
    assert len(body['data']['events']) > 0
    num = random.choice(body['data']['events'])
    actual_start = num['eventStartTime']
    actual_end = num['eventEndTime']
    actual = int(actual_end) - int(actual_start)
    expect = 1602291000 - 1602210000
    assert actual >= expect
    print('测试通过：实际日历区间:{},期望日历区间:{}'.format(actual, expect))


@allure.suite('calendar')
@allure.title('BM车机端获取用户事件列表')
@pytest.mark.calendar
def test_get_event_list_03():
    '''
    查询指定时间段时间列表,输入时间区间错误
    '''
    data = {'apiType': 'TYPE_ONE', 'startDate': '16022050000', 'endDate': '1602291000'}
    body = c.get_event_list(data)
    assert body['errorMessage'] == 'wrong date range'


@allure.suite('calendar')
@allure.title('BM车机端获取用户事件列表')
@pytest.mark.calendar
def test_get_event_list_04():
    '''
    查询指定时间段时间列表,输入枚举值错误
    '''
    data = {'apiType': 'TYPE_ONE1', }
    body = c.get_event_list(data)
    assert body['errorCode'] == '400'


@pytest.mark.calendar
@allure.suite('calendar')
@allure.title('BM车机端获取用户最后更新时间')
@pytest.mark.parametrize('uid', [c.uid, '123456', '4606930', '4608048', '4608147'])
def test_get_last_time(uid):
    '''
    获取日历最近一次更新时间
    '''
    body = c.get_last_time(uid, c.device_id)
    assert body['data']['updateTime'] is not None


@pytest.mark.calendar
@allure.suite('calendar')
@allure.title('rrule_list')
@pytest.mark.parametrize('api', ['TYPE_ONE', 'TYPE_TWO', 'TYPE_THREE'])
def test_event_list_by_rule_01(api):
    '''
    测试根据规则返回日历事件列表
    '''
    st = 1602401995000
    et = 1603427680000
    device = c.device_id
    params = c.do_mysql_select('select uid from calendar_event where rrule="FREQ=DAILY;COUNT=2"', 'fawvw_calendar')
    uid = params[0]['uid']
    body = c.event_list_by_rule(api, st, et, uid, device)
    print(body)


@pytest.mark.calendar
@allure.suite('calendar')
@allure.title('mobile')
@pytest.mark.parametrize('cud', ['C', 'U'])
def test_mobile_sync_01(cud):
    '''
    输入一个event，同步事件,cud为C或者D
    '''
    l_id = c.f.pyint(100, 1000)
    mobile_event = {'localEventId': l_id, 'cudStatus': cud,
                    'eventStartTime': c.get_time_stamp(days=-10), 'eventEndTime': c.get_time_stamp(days=10)}
    time = c.get_time_stamp()
    res = c.mobile_sync(time,[mobile_event])
    assert res['data']['syncCounts'] == 1
    sql_res = c.do_mysql_select('select * from calendar_event where uid="{}" and local_event_id="{}"'.format(c.uid,l_id),'fawvw_calendar')
    assert sql_res[0]['origin'] == 'APP'

@pytest.mark.calendar
@allure.suite('calendar')
@allure.title('mobile')
def test_mobile_sync_02():
    '''
    输入多个event，同步事件
    '''
    mobile_event1 = {'localEventId': c.f.pyint(100, 1000), 'cudStatus': 'C',
                     'eventStartTime': c.get_time_stamp(days=-10), 'eventEndTime': c.get_time_stamp(days=10)}

    mobile_event2 = {'localEventId': c.f.pyint(100, 1000), 'cudStatus': 'U',
                     'eventStartTime': c.get_time_stamp(seconds=10), 'eventEndTime': c.get_time_stamp(seconds=20)}
    mobile_event3 = {'localEventId': c.f.pyint(100, 1000), 'cudStatus': 'C',
                     'eventStartTime': c.get_time_stamp(seconds=10), 'eventEndTime': c.get_time_stamp(seconds=20),
                     'remarks': c.f.sentence(),'allday':False}
    time = c.get_time_stamp()
    res = c.mobile_sync(time,[mobile_event1,mobile_event2,mobile_event3])
    assert res['data']['syncCounts'] == '3'


@pytest.mark.calendar
@allure.suite('calendar')
@allure.title('app端查看用户所有日历事件')
def test_mobile_find_all():
    res = c.mobile_find_all()
    sql_res = c.do_mysql_select('select count(1) as events from calendar_event where uid ="{}" and origin="APP"'.format(c.uid),'fawvw_calendar')
    assert len(res['events']) == sql_res[0]['events']

