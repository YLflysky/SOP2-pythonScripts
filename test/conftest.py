import os
from order.payment import Payment
from order.order_api import Order
from order.bm_order import BMOrder
from order.bm_payment import BMPayment
from flow.flow import Flow
from app.app_api import App

if not os.getenv('GATE'):
    os.environ['GATE'] = 'false'
if not os.getenv('ENV'):
    os.environ['ENV'] = 'SIT'

pay = Payment()
order = Order()
bm_pay = BMPayment()
bm_order = BMOrder()
flow = Flow()

name = '13353116624'
password = '000000'
aid = '9353497'

vins = [('LFVSOP2TESTLY0003','SOP2BM'),
        ('LFVSOP2TESTLY0002','SOP2MA'),
        ('LFVSOP2TESTLY0010','37W'),
        ('LFVSOP2TESTLY0097','MEB'),
        ('LFVSOP2TESTLY0011','SOP1')]

app = App(name,password,aid=aid)

app_xmly = App(name='13353110073',password='000000',aid='9354046')






