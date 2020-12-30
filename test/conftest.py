import os

if not os.getenv('GATE'):
    os.environ['GATE'] = 'false'
if not os.getenv('ENV'):
    os.environ['ENV'] = 'DEV'




