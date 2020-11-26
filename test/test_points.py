import pytest
import allure
import random
import sys, os
import json

from point.points import Points
from box.lk_logger import lk

p = Points()


@allure.suite('points')
@allure.title('底层获取积分')
@pytest.mark.points
def test_get_user_level():
    res = p.get_user_level(aid='123',system_key='267C13173FE04A57AX',tenant='VW')
    assert res['returnStatus'] == 'SUCCEED'
    assert res['data']['memberLevel']