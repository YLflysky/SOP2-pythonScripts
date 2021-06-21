import os
from order import *
from flow.flow import Flow
from app.app_api import App
from eshop.eshop import PointsShop,SpareShop
from eshop.smart_shop import SmartEShop
from calendar_file.canlendar_api import Calendar
from ma_api import *
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


ma_order_adapter = ma_order_adapter.MAOrderAdapter(aid,user,password,vin,token=False)
bonus = PointsShop(tenant='MA',token=False)
spare = SpareShop('MA',token=False)
ma_shop = SmartEShop(tenant='MA',token=False)
ma_calendar = Calendar(tenant='MA',token=False)
ma_car = tencent_car.TencentCar(aid,user,password,vin,False)
ma_group_driving = team.Team(aid,user,password,vin,False)
ma_pay = ma_pay.MAPay(aid,user,password,vin,False)
sop1_order = sop1_order.SOP1Order(aid,user,password,vin,False)

bonus.header['authorization'] = token
spare.header['authorization'] = token
ma_shop.header['authorization'] = token
ma_calendar.header['authorization'] = token
ma_pay.header['authorization'] = token
ma_order_adapter.header['authorization'] = token
ma_group_driving.header['authorization'] = token
ma_car.header['authorization'] = token
sop1_order.header['authorization'] = token

ma_order = ma_order.MAOrder()
pay = payment.Payment()
order = order_api.Order()
bm_pay = bm_payment.BMPayment()
bm_order = bm_order.BMOrder()
flow = Flow()

vins = [('LFVSOP2TESTLY0003','SOP2BM'),
        ('LFVSOP2TESTLY0002','SOP2MA'),
        ('LFVSOP2TESTLY0010','37W'),
        ('LFVSOP2TESTLY0097','MEB'),
        ('LFVSOP2TESTLY0011','SOP1')]

app = App(user,password,aid=aid)







