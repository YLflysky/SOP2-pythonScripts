import pytest
from box.base import Base
import os
from box.lk_logger import lk

if not os.getenv('GATE'):
    os.environ['GATE'] = 'false'
if not os.getenv('ENV'):
    os.environ['ENV'] = 'UAT'




