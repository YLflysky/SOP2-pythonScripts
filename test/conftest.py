import pytest
from box.base import Base
import os
o = Base()

if not os.getenv('GATE'):
    os.environ['GATE'] = 'false'
if not os.getenv('ENV'):
    os.environ['ENV'] = 'UAT'

