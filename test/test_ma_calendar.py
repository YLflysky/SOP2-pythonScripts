import pytest
from calendar_file.canlendar_api import Calendar
import allure
import random

c = Calendar(tenant='MA',name='18280024450',password='Qq111111',aid='9350195',vin='LFVSOP2TEST000311')


@pytest.fixture()
def set_up_add_event():
    start_time = c.get_time_stamp(days=1)
    end_time = c.get_time_stamp(days=2)
    # 新建日历事件
    res = c.add_event(start_time=start_time, end_time=end_time)
    return res['data']['id']

@allure.suite('ma-calendar')
@allure.title('MA车机端获取用户所有日历事件')
@pytest.mark.calendar
def test_find_all():
    res = c.find_all_event(update_time=None)
    assert res['data']['events']


@allure.suite('ma-calendar')
@allure.title('MA车机端获取用户单个日历详情')
@pytest.mark.calendar
def test_find_detail(set_up_add_event):
    res = c.find_detail(id=set_up_add_event)
    assert res['data']['origin'] == 'HU'


@allure.suite('ma-calendar')
@allure.title('MA车机端删除用户日历事件')
@pytest.mark.calendar
def test_del_event(set_up_add_event):
    c.del_event(event_id=set_up_add_event)


@allure.suite('ma-calendar')
@allure.title('MA车机端更新用户日历事件')
@pytest.mark.calendar
def test_update_event(set_up_add_event):
    s = c.get_time_stamp(days=2)
    e = c.get_time_stamp(days=3)
    c.update_event(set_up_add_event,s=s,e=e)


@pytest.mark.calendar
@allure.suite('ma-calendar')
@allure.title('MA车机端获取用户最后更新时间')
@pytest.mark.parametrize('uid', [c.uid, '123456', '4606930', '4608048', '4608147'])
def test_get_last_time(uid):
    '''
    获取日历最近一次更新时间
    '''
    body = c.get_last_time(uid, deviceId=c.tenant)
    assert body['data']['updateTime'] is not None


@allure.suite('ma-calendar')
@allure.title('MA车机端获取用户事件列表，根据apiType')
@pytest.mark.calendar
@pytest.mark.parametrize('t', ['TYPE_ONE', 'TYPE_TWO', 'TYPE_THREE'])
def test_get_event_list_type(t):
    '''
    查询指定时间段时间列表,仅输入apiType
    '''
    data = {'apiType': t}
    body = c.get_event_list(data)
    assert len(body['data']['events']) > 0


@allure.suite('ma-calendar')
@allure.title('MA车机端获取用户事件列表，根据开始结束时间')
@pytest.mark.calendar
def test_get_event_list_date():
    '''
    查询指定时间段时间列表,输入Date
    '''
    start = 1598240339000
    end = 1598240340000
    data = {'apiType': 'TYPE_ONE', 'startDate': start, 'endDate': end}
    body = c.get_event_list(data)
    assert len(body['data']['events']) > 0
    num = random.choice(body['data']['events'])
    actual_start = num['eventStartTime']
    actual_end = num['eventEndTime']
    actual = int(actual_end) - int(actual_start)
    expect = end - start
    assert actual <= expect
    print('测试通过：实际日历区间:{},期望日历区间:{}'.format(actual, expect))


@allure.suite('ma-calendar')
@allure.title('MA车机端新增用户日历事件')
@pytest.mark.calendar
def test_add_event_01():
    '''
    输入全部必填项，添加日历事件
    '''
    start_time = c.get_time_stamp(days=10)
    end_time = c.get_time_stamp(days=11)

    calendar_id = c.add_event(start_time, end_time)['data']['id']
    try:
        detail = c.find_detail(calendar_id)
        assert str(detail['data']['eventStartTime']) == start_time
        assert str(detail['data']['eventEndTime']) == end_time
    finally:
        c.del_event(event_id=calendar_id)


@allure.suite('ma-calendar')
@allure.title('MA车机端新增用户日历事件')
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

    try:
        res = c.find_detail(calendar_id)
        assert res['data']['allday'] == True
        assert res['data']['origin'] == 'HU'
        assert res['data']['address'] == address
        assert res['data']['localEventId'] == str(local_event_id)
        assert res['data']['remarks'] == remarks
        assert res['data']['longitude'] == 123.0
        assert res['data']['latitude'] == 23.0
    finally:
        c.del_event(event_id=calendar_id)


@allure.suite('ma-calendar')
@allure.title('MA车机端新增用户日历事件')
@pytest.mark.calendar
def test_add_event_03():
    '''
    输入开始时间在结束时间之后，报错
    '''
    s = c.get_time_stamp(days=2)
    e = c.get_time_stamp(days=1)
    body = c.add_event(s, e)

    assert body['statusMessage'] == 'wrong date range'


@allure.suite('ma-calendar')
@allure.title('MA车机端新增用户日历事件')
@pytest.mark.calendar
def test_add_event_04():
    '''
    传入rrule
    '''
    s = c.get_time_stamp(days=-100)
    e = c.get_time_stamp(days=100)
    id = c.add_event(s, e, rrule='Only Once')['data']['id']
    detail = c.find_detail(id)

    assert detail['data']['rrule'] == 'Only Once'


@allure.suite('ma-calendar')
@allure.title('MA车机端新增用户日历事件')
@pytest.mark.calendar
def test_add_event_05():
    '''
    传入错误的rrule
    '''
    s = c.get_time_stamp(days=2)
    e = c.get_time_stamp(days=3)
    body = c.add_event(s, e, rrule='Only Once1')
    assert body['statusMessage'] == 'rule resolve error'


@pytest.mark.calendar
@allure.suite('ma-calendar')
@allure.title('APP同步MA用户日历事件')
@pytest.mark.parametrize('cud', ['C', 'U', 'D'])
def test_mobile_sync_01(cud):
    '''
    输入一个event，同步事件
    '''
    mobile_event = {'localEventId': c.f.pyint(100, 1000), 'cudStatus': cud,
                    'eventStartTime': c.get_time_stamp(days=-10), 'eventEndTime': c.get_time_stamp(days=10)}
    time = c.get_time_stamp()
    res = c.mobile_sync(time,[mobile_event])
    assert res['data']['syncCounts'] == 1
