import pytest
from box.base import Base
import os
from box.lk_logger import lk

if not os.getenv('GATE'):
    os.environ['GATE'] = 'false'
if not os.getenv('ENV'):
    os.environ['ENV'] = 'UAT'

b = Base()


@pytest.fixture(scope='session')
def get_ma_token():
    '''
    获取MA项目车机端token
    :return:
    '''
    lk.prt('当前测试环境为:{}'.format(os.getenv('ENV')))
    url = b.read_conf('ma_env.conf','UAT','token_host')
    token = b.get_token(url,username='18224077254',password='123456',vin='LFV3A23C1K3161804')
    return token



