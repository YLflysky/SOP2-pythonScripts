import random
from eshop.eshop import PointsShop,SpareShop
from eshop.smart_shop import SmartEShop
from calendar_file.canlendar import Calendar
from box.base import Base

b = Base()


token_url = b.read_conf('ma_env.conf','UAT','token_host')
user = b.read_yml('../../conf','user.yml')
user = user['user_ma']
token = b.get_token(token_url,user['user'],user['password'],user['vin'])


bonus = PointsShop(tenant='MA',token=False)
spare = SpareShop('MA',token=False)
ma_shop = SmartEShop(tenant='MA',token=False)
ma_calendar = Calendar(tenant='MA',token=False)


bonus.header['authorization'] = token
spare.header['authorization'] = token
ma_shop.header['authorization'] = token
ma_calendar.header['authorization'] = token






