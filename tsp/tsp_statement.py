from box.base import Base
from box.redis_utils import RedisUtils
import os,json
from requests_toolbelt.multipart.encoder import MultipartEncoder

class Statement(Base):
    def __init__(self):
        super().__init__()
        self.url = self.read_conf('ftb3_env.conf',self.env,'statement_host')
        self.header['username'] = 'sergio'
        self.header['userId'] = '4614183'
        self.header['brand'] = 'VW'

    def statement_list(self,third_name,**kwargs):
        url = self.url + '/statement/list'
        data = {'thirdName':third_name,**kwargs}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def item_list(self,s_no,**kwargs):
        '''
        对账单明细列表
        '''
        url = self.url + '/statement/items'
        data = {'statementNo':s_no,**kwargs}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def item_check(self,s_no,s_c_no,s_m_amount,s_r_no,remarks):
        '''
        对账单差异核对
        '''

        url = self.url + '/statement/check'
        data = {'statementNo':s_no,'statementCheckNo':s_c_no,'settleMoneyAmount':s_m_amount,'settleRecordNum':s_r_no,'remarks':remarks}
        # self.header['aid'] = '4614183'
        # self.header['username'] = '4614183'
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def generate_statement(self,cp,s_time,percent_platform,s_p_type,s_type,if_cp=False):
        '''
        生成对账单
        '''
        # self.header['username'] = 'sergio'
        # self.header['userId'] = '4614183'
        # self.header['brand'] = 'VW'
        url = self.url + '/statement/generate'
        data = {'thirdName':cp,'statementTime':s_time,'platformProportion':percent_platform,
                'statementPeriodType':s_p_type,'statementType':s_type,'needThirdStatement':if_cp}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)

    def cp_file(self,file_path,file_name,sp,s_time,s_type,s_p_type,**kwargs):
        '''
        导入cp文件接口
        '''

        param = {'file': file_name, 'thirdName': sp, 'statementTime': s_time,
                 'statementType': s_type,'statementPeriodType':s_p_type,**kwargs}

        multipart_encoder = MultipartEncoder(
            fields={

                'file':(file_name,open(file_path,'rb'),'application/vnd.ms-excel'),
                'params': (None,json.dumps(param),'application/json'),
            }, boundary='-----------------------------2385610611750'
        )
        self.header['Content-Type'] = multipart_encoder.content_type
        # self.header['username'] = 'sergio'
        # self.header['userId'] = '4614183'
        # self.header['brand'] = 'VW'
        url = self.url + '/statement/file/upload'
        c,b = self.do_post_multipart(url,data=multipart_encoder)
        self.assert_msg(c,b)

    def query_base_info(self,key):
        '''
        基础配置信息查询
        '''
        url = self.url + '/statement/dict'
        data = {'dictKeys':key}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':

    os.environ['ENV'] = 'DEV'
    os.environ['GATE'] = 'false'
    s = Statement()
    redis_util = RedisUtils()
    s.query_base_info(key='spName')
    # s.cp_file(file_path='../data/JD_OPEN导入账单.xlsx', file_name='sergio', sp='JD_OPEN', s_time='2020-05-01 00:00:00', s_type='ORDER_STATEMENT', s_p_type='MONTH')
    # redis_util.get_hash_value(key='bill:check_record_map:third:JD_OPEN:ORDER_STATEMENT:20200501000000:false')
    # s.generate_statement(cp='JD_OPEN',s_time='2021-05-05 00:00:00',percent_platform=10,s_p_type='MONTH',s_type='PAY_STATEMENT')
    # s.statement_list(third_name='JD_OPEN',beginTime=s.time_delta(days=-15),statementStatus=None)
    # s.item_list(s_no='DZD20210510102459819393216',status='UNCHECK')
    # s.item_check(s_no='DZD20210510102459819393216',s_c_no='2',s_m_amount=99.00,s_r_no=1,remarks='jojo')
    # print(redis_util.conn.mget('bill:check_set:platform:KUWO:PAY_STATEMENT:20210501000000:false'))