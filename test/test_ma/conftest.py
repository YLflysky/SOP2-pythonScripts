import random
from eshop.eshop import PointsShop,SpareShop
from eshop.smart_shop import SmartEShop
from calendar_file.canlendar import Calendar
from ma_api.ma_order import MAOrder
from ma_api.ma_order_adapter import MAOrderAdapter
from box.base import Base

b = Base()


token_url = b.read_conf('ma_env.conf','UAT','token_host')
aid = ''
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

bonus.header['authorization'] = token
spare.header['authorization'] = token
ma_shop.header['authorization'] = token
ma_calendar.header['authorization'] = token
ma_order.header['authorization'] = token
ma_order_adapter.header['authorization'] = token






