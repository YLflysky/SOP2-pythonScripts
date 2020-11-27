import pytest
import allure
import random
import sys, os
import json

from point.points import Points
from box.lk_logger import lk

p = Points()


@allure.suite('points')
@allure.title('底层获取用户积分等级')
@pytest.mark.points
def test_get_user_level():
    res = p.get_user_level(aid='123',system_key='267C13173FE04A57AX',tenant='VW')
    assert res['returnStatus'] == 'SUCCEED'
    assert res['data']['memberLevel']
    lk.prt('测试获取用户积分等级成功')


@allure.suite('points')
@allure.title('底层获取用户剩余积分数')
@pytest.mark.points
def test_get_user_points():
    res = p.get_user_points(aid='123')
    assert res['returnStatus'] == 'SUCCEED'
    assert res['data'][0]['remainScore']


@allure.suite('points')
@allure.title('底层获取用户积分使用明细')
@pytest.mark.points
def test_get_user_points():
    index = 1
    size = random.randint(1,10)
    res = p.get_points_stream(index,size,aid='123')
    assert res['returnStatus'] == 'SUCCEED'
    length = len(res['data'])
    if length<=size:
        assert length == res['totalCount']
    else:
        assert length == size


@allure.suite('points')
@allure.title('BM车机端获取用户剩余积分')
@pytest.mark.points
@pytest.mark.parametrize('aid',['123','1234'])
def test_bm_get_user_points(aid):
    res = p.bm_get_user_points(aid)
    res1 = p.get_user_points(aid)
    assert res['data']['point'] == res1['data'][0]['remainScore']
    lk.prt('获取用户剩余积分为->{}:{}'.format(aid,res['data']['point']))