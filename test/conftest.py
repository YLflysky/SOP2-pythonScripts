import pytest
from box.base import Base
from order.bm_order import BMOrder
import os


if not os.getenv('GATE'):
    os.environ['GATE'] = 'false'
if not os.getenv('ENV'):
    os.environ['ENV'] = 'UAT'

o = Base()
bm = BMOrder()

@pytest.fixture()
def reload_category_relation_config():
    bm.reload_config()

