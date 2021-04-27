import os
from order.payment import Payment
from order.order_api import Order
from order.bm_order import BMOrder
from order.bm_payment import BMPayment
from flow.flow import Flow
from app.app_api import App
from eshop.eshop import PointsShop,SpareShop
from eshop.smart_shop import SmartEShop
from calendar_file.canlendar_api import Calendar
from ma_api.ma_order import MAOrder
from ma_api.ma_pay import MAPay
from ma_api.sop1_order import SOP1Order
from ma_api.ma_order_adapter import MAOrderAdapter
from ma_api.tencent_car import TencentCar
from ma_api.team import Team
from box.base import Base

if not os.getenv('GATE'):
    os.environ['GATE'] = 'false'
if not os.getenv('ENV'):
    os.environ['ENV'] = 'SIT'

b = Base()


token_url = b.read_conf('ma_env.conf','UAT','token_host')
aid = '4614183'
user = '15330011918'
password = '000000'
vin = 'LFVTEST1231231231'
token = b.get_token(token_url,user,password,vin)


ma_order_adapter = MAOrderAdapter(aid,user,password,vin,token=False)
bonus = PointsShop(tenant='MA',token=False)
spare = SpareShop('MA',token=False)
ma_shop = SmartEShop(tenant='MA',token=False)
ma_calendar = Calendar(tenant='MA',token=False)
ma_car = TencentCar(aid,user,password,vin,False)
ma_group_driving = Team(aid,user,password,vin,False)
ma_pay = MAPay(aid,user,password,vin,False)
sop1_order = SOP1Order(aid,user,password,vin,False)

bonus.header['authorization'] = token
spare.header['authorization'] = token
ma_shop.header['authorization'] = token
ma_calendar.header['authorization'] = token
ma_pay.header['authorization'] = token
ma_order_adapter.header['authorization'] = token
ma_group_driving.header['authorization'] = token
ma_car.header['authorization'] = token
sop1_order.header['authorization'] = token

ma_order = MAOrder()
pay = Payment()
order = Order()
bm_pay = BMPayment()
bm_order = BMOrder()
flow = Flow()

vins = [('LFVSOP2TESTLY0003','SOP2BM'),
        ('LFVSOP2TESTLY0002','SOP2MA'),
        ('LFVSOP2TESTLY0010','37W'),
        ('LFVSOP2TESTLY0097','MEB'),
        ('LFVSOP2TESTLY0011','SOP1')]

app = App(user,password,aid=aid)







