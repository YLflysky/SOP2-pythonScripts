import pytest
from box.base import Base
from order.bm_order import BMOrder
from flow.flow_api import Flow
from order.payment import Payment
import os
from box.lk_logger import lk

if not os.getenv('GATE'):
    os.environ['GATE'] = 'false'
if not os.getenv('ENV'):
    os.environ['ENV'] = 'DEV'


def setup_module():
    lk.prt('当前测试环境为:{}'.format(os.getenv('ENV')))

bm = BMOrder()

@pytest.fixture()
def reload_category_relation_config():
    bm.reload_config()


