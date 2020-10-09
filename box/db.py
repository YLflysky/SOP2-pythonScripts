
from enum import Enum


class MysqlConfig(Enum):
    SIT_HOST = '192.168.133.142'
    SIT_PORT = 3306
    SIT_USER = 'faw_ep_sit_rd'
    SIT_PASSWORD = 'GyDb06V8qmMhOxWZ5NaB'
    EP_SIT = {'host':'192.168.133.142','port':3306,'username':'faw_ep_sit_rd','password':'GyDb06V8qmMhOxWZ5NaB'}
    AP_DEV = {'host':'10.20.6.10','port':3306,'username':'root','password':'Cdp@123@mysql'}
    EP_UAT = {'host':'10.20.14.8','port':3306,'username':'faw_ep_uat_rd_r','password':'EZHNoaUYBgPvTXnxiy5S'}
    EP_DEV = {'host':'10.20.14.4','port':3306,'username':'faw_ep_dev','password':'if1dNu3lK9z4pXBTWojq'}
    EP_LOCAL = EP_DEV
    SOP2_MA=EP_UAT

# print(MysqlConfig.SIT.value)
