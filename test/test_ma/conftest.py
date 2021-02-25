import random
from eshop.eshop import PointsShop,SpareShop
from eshop.smart_shop import SmartEShop
from calendar_file.canlendar import Calendar
from box.base import Base

b = Base()


token_url = b.read_conf('ma_env.conf','UAT','token_host')
# conf_dir = b.get_pro_path() + '/conf'
# user = b.read_yml(conf_dir,'user.yml')
# user = user['user_ma']
token = b.get_token(token_url,'15566938326','test1234','TESTWECHAT6026067')


bonus = PointsShop(tenant='MA',token=False)
spare = SpareShop('MA',token=False)
ma_shop = SmartEShop(tenant='MA',token=False)
ma_calendar = Calendar(tenant='MA',token=False)

bonus.header['authorization'] = token
spare.header['authorization'] = token
ma_shop.header['authorization'] = token
ma_calendar.header['authorization'] = token






