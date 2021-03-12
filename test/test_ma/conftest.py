import random
from eshop.eshop import PointsShop,SpareShop
from eshop.smart_shop import SmartEShop
from calendar_file.canlendar import Calendar
from ma_api.ma_order import MAOrder
from ma_api.ma_order_adapter import MAOrderAdapter
from ma_api.tencent_car import TencentCar
from ma_api.team import Team
from box.base import Base

b = Base()


token_url = b.read_conf('ma_env.conf','UAT','token_host')
aid = '4614183'
user = '15330011918'
password = '000000'
vin = 'LFVTEST1231231231'
token = b.get_token(token_url,user,password,vin)

ma_order = MAOrder(aid,user,password,vin,token=False)
ma_order_adapter = MAOrderAdapter(aid,user,password,vin,token=False)
bonus = PointsShop(tenant='MA',token=False)
spare = SpareShop('MA',token=False)
ma_shop = SmartEShop(tenant='MA',token=False)
ma_calendar = Calendar(tenant='MA',token=False)
ma_car = TencentCar(aid,user,password,vin,False)
ma_group_driving = Team(aid,user,password,vin,False)

bonus.header['authorization'] = token
spare.header['authorization'] = token
ma_shop.header['authorization'] = token
ma_calendar.header['authorization'] = token
ma_order.header['authorization'] = token
ma_order_adapter.header['authorization'] = token
ma_group_driving.header['authorization'] = token
ma_car.header['authorization'] = token






