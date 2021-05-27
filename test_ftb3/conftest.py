from tsp.tsp_statement import Statement
from box.lk_logger import lk
import os

if not os.getenv('ENV'):
    os.environ['ENV'] = 'DEV'
if not os.getenv('GATE'):
    os.environ['GATE'] = 'false'

s = Statement()