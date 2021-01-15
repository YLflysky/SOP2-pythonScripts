
from enum import Enum


class MysqlConfig(Enum):
    SIT_HOST = '192.168.133.142'
    SIT_PORT = 3306
    SIT_USER = 'faw_ep_sit_rd'
    SIT_PASSWORD = 'GyDb06V8qmMhOxWZ5NaB'
    EP_SIT = {'host':'192.168.133.142','port':3306,'username':'faw_ep_sit_rd','password':'GyDb06V8qmMhOxWZ5NaB'}
    # EP_UAT = {'host':'10.20.14.8','port':3306,'username':'faw_ep_uat_rd_r','password':'EZHNoaUYBgPvTXnxiy5S'}
    EP_DEV = {'host':'10.20.14.4','port':3306,'username':'faw_sop2_dev','password':'GURVzuQcTIJ5Z8DL#2dl'}
    EP_LOCAL = EP_DEV
    SOP2_MA=EP_DEV
    EP_UAT = EP_DEV
    SOP2_DEV = {'host':'192.168.133.191','port':3306,'username':'faw_sop2_dev','password':'oJNqwQsUa239GbdYz7Tp'}
    SOP2_SIT = {'host':'192.168.133.178','port':3306,'username':'faw_sop2_sit','password':'d5Au97KWFXH@MGQk3fcU'}
    SOP2_UAT = {'host':'192.168.133.203','port':3306,'username':'faw_sop2_uat_rd_automation','password':'ci1yjxz4qIuNpJZCOHrR'}
    SOP2_LOCAL = SOP2_DEV
    MA_UAT = {'host':'192.168.162.199','port':3306,'username':'MosUatUser','password':'YmUwMDAzYmhNWFiZT'}
    MA_DEV = {'host':'192.168.162.199','port':3306,'username':'MosUatUser','password':'YmUwMDAzYmhNWFiZT'}
    MA_SIT = {'host':'192.168.162.199','port':3306,'username':'MosUatUser','password':'YmUwMDAzYmhNWFiZT'}
# print(MysqlConfig.SIT.value)

class KafkaConfig(Enum):
    EP_DEV = '10.20.4.12:9092'
    EP_SIT = '192.168.133.136:9092'
    EP_UAT = '10.20.4.11:9092'
    SOP2_DEV = '192.168.133.168:9092'
    SOP2_SIT = '192.168.133.176:9092'
    SOP2_UAT = '192.168.133.173:9092'
    MA_UAT = '10.224.32.50:9092'