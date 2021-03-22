import pytest
from ..conftest import ma_calendar
import allure
import random


@pytest.fixture()
def set_up_add_event():
    start_time = ma_calendar.get_time_stamp(days=1)
    end_time = ma_calendar.get_time_stamp(days=2)
    # 新建日历事件
    res = ma_calendar.add_event(start_time=start_time, end_time=end_time)
    return res['data']['id']

@allure.suite('test_ma-calendar')
@allure.title('MA车机端获取用户所有日历事件')
@pytest.mark.ma_calendar
def test_find_all():
    res = ma_calendar.find_all_event(update_time=None)
    assert res['data']['events']


@allure.suite('test_ma-calendar')
@allure.title('MA车机端获取用户单个日历详情')
@pytest.mark.ma_calendar
def test_find_detail(set_up_add_event):
    res = ma_calendar.find_detail(id=set_up_add_event)
    assert res['data']['origin'] == 'HU'


@allure.suite('test_ma-calendar')
@allure.title('MA车机端删除用户日历事件')
@pytest.mark.ma_calendar
def test_del_event(set_up_add_event):
    ma_calendar.del_event(event_id=set_up_add_event)


@allure.suite('test_ma-calendar')
@allure.title('MA车机端更新用户日历事件')
@pytest.mark.ma_calendar
def test_update_event(set_up_add_event):
    s = ma_calendar.get_time_stamp(days=2)
    e = ma_calendar.get_time_stamp(days=3)
    ma_calendar.update_event(set_up_add_event,s=s,e=e)


@pytest.mark.ma_calendar
@allure.suite('test_ma-calendar')
@allure.title('MA车机端获取用户最后更新时间')
def test_get_last_time():
    '''
    获取日历最近一次更新时间
    '''
    body = ma_calendar.get_last_time()
    assert body['data']['updateTime'] is not None


@allure.suite('test_ma-calendar')
@allure.title('MA车机端获取用户事件列表，根据apiType')
@pytest.mark.ma_calendar
@pytest.mark.parametrize('t', ['TYPE_ONE', 'TYPE_TWO', 'TYPE_THREE'])
def test_get_event_list_type(t):
    '''
    查询指定时间段时间列表,仅输入apiType
    '''
    data = {'apiType': t}
    body = ma_calendar.get_event_list(data)
    assert len(body['data']['events']) > 0


@allure.suite('test_ma-calendar')
@allure.title('MA车机端获取用户事件列表，根据开始结束时间')
@pytest.mark.ma_calendar
def test_get_event_list_date():
    '''
    查询指定时间段时间列表,输入Date
    '''
    start = 1599466345000
    end = 1616746345000
    data = {'apiType': 'TYPE_ONE', 'startDate': start, 'endDate': end}
    body = ma_calendar.get_event_list(data)
    assert len(body['data']['events']) > 0
    num = random.choice(body['data']['events'])
    actual_start = num['eventStartTime']
    actual_end = num['eventEndTime']
    actual = int(actual_end) - int(actual_start)
    expect = end - start
    assert actual <= expect
    print('测试通过：实际日历区间:{},期望日历区间:{}'.format(actual, expect))


@allure.suite('test_ma-calendar')
@allure.title('MA车机端新增用户日历事件>>输入必填项')
@pytest.mark.ma_calendar
def test_add_event_01():
    '''
    输入全部必填项，添加日历事件
    '''
    start_time = ma_calendar.get_time_stamp(days=10)
    end_time = ma_calendar.get_time_stamp(days=11)

    calendar_id = ma_calendar.add_event(start_time, end_time)['data']['id']
    try:
        detail = ma_calendar.find_detail(calendar_id)
        assert str(detail['data']['eventStartTime']) == start_time
        assert str(detail['data']['eventEndTime']) == end_time
    finally:
        ma_calendar.del_event(event_id=calendar_id)


@allure.suite('test_ma-calendar')
@allure.title('MA车机端新增用户日历事件>>输入全部参数')
@pytest.mark.ma_calendar
def test_add_event_02():
    '''
    输入全部必填项，输入全部选填项
    '''
    start_time = ma_calendar.get_time_stamp(days=10)
    end_time = ma_calendar.get_time_stamp(days=11)
    event_name = ma_calendar.f.word()
    address = ma_calendar.f.address()
    longitude = '123.00'
    latitude = '23.00'
    remarks = ma_calendar.f.sentence()
    allday = True
    create_time = ma_calendar.get_time_stamp()
    duration = '123'
    local_event_id = ma_calendar.f.pyint()

    calendar_id = ma_calendar.add_event(start_time, end_time,
                              localEventId=local_event_id,
                              eventName=event_name,
                              address=address,
                              longitude=longitude, latitude=latitude, remarks=remarks,
                              duration=duration, createTime=create_time, allday=allday)['data']['id']

    try:
        res = ma_calendar.find_detail(calendar_id)
        assert res['data']['allday'] == True
        assert res['data']['origin'] == 'HU'
        assert res['data']['address'] == address
        assert res['data']['localEventId'] == str(local_event_id)
        assert res['data']['remarks'] == remarks
        assert res['data']['longitude'] == 123.0
        assert res['data']['latitude'] == 23.0
    finally:
        ma_calendar.del_event(event_id=calendar_id)


@allure.suite('test_ma-calendar')
@allure.title('MA车机端新增用户日历事件>>输入开始时间在结束时间之后，报错')
@pytest.mark.ma_calendar
def test_add_event_03():
    '''
    输入开始时间在结束时间之后，报错
    '''
    s = ma_calendar.get_time_stamp(days=2)
    e = ma_calendar.get_time_stamp(days=1)
    body = ma_calendar.add_event(s, e)
    assert body['statusCode'] == '5004'
    assert body['statusMessage'] == 'wrong date range'


@allure.suite('test_ma-calendar')
@allure.title('MA车机端新增用户日历事件>>传入rrule为Only Once')
@pytest.mark.ma_calendar
def test_add_event_04():
    '''
    传入rrule
    '''
    s = ma_calendar.get_time_stamp(days=-100)
    e = ma_calendar.get_time_stamp(days=100)
    id = ma_calendar.add_event(s, e, rrule='Only Once')['data']['id']
    detail = ma_calendar.find_detail(id)

    assert detail['data']['rrule'] == 'Only Once'


@allure.suite('test_ma-calendar')
@allure.title('MA车机端新增用户日历事件>>传入错误的rrule，报错')
@pytest.mark.ma_calendar
def test_add_event_05():
    '''
    传入错误的rrule
    '''
    s = ma_calendar.get_time_stamp(days=2)
    e = ma_calendar.get_time_stamp(days=3)
    body = ma_calendar.add_event(s, e, rrule='Only Once1')
    assert body['statusMessage'] == 'rule resolve error'



