from box.base import Base
from box.lk_logger import lk
from box.redis_utils import RedisUtils
import os,json
from requests_toolbelt.multipart.encoder import MultipartEncoder

class Statement(Base):
    def __init__(self):
        super().__init__()
        self.url = self.read_conf('ftb3_env.conf',self.env,'market_host') + '/bill'
        self.header['username'] = 'sergio'
        self.header['userId'] = '4614183'
        self.header['brand'] = 'VW'

    def statement_list(self,third_name,**kwargs):
        url = self.url + '/statement/list'
        data = {'thirdName':third_name,**kwargs}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

    def item_list(self,s_no,page_no=1,page_size=20,**kwargs):
        '''
        对账单明细列表
        '''
        url = self.url + '/statement/items'
        param = {'pageNo':page_no,'pageSize':page_size}
        data = {'statementNo':s_no,**kwargs}
        c,b = self.do_post(url,data,params=param)
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
        url = self.url + '/statement/generate'
        data = {'thirdName':cp,'statementTime':s_time,'platformProportion':percent_platform,
                'statementPeriodType':s_p_type,'statementType':s_type,'needThirdStatement':if_cp}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)
        return b

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

    def fail_cp_upload(self,sp,s_time,s_type,s_p_type='MONTH'):
        '''
        导入失败文件导出
        '''

        url = self.url + '/statement/uploadFailFile/download'
        data = {'thirdName':sp,'statementTime':s_time,'statementType':s_type,'statementPeriodType':s_p_type}
        c,b = self.do_get(url,data,stream=True)
        # self.assert_msg(c,b)

    def confirm_statement(self,s_no):
        '''
        确认账单
        '''
        url = self.url + '/statement/confirm'
        data = {'statementNo':s_no}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)

    def abandon_statement(self,s_no,reason):
        '''
        废弃账单
        '''
        url = self.url + '/statement/cancel'
        data = {'statementNo':s_no,'cancelReason':reason}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)

    def upload_statement_diff(self,s_no):
        '''
        导出对账单差异明细
        '''
        url = self.url + '/statement/diff/download'
        data = {'statementNo':s_no}
        c,b = self.do_get_stream(url,data)
        assert c == 200
        with open('../data/{}.xlsx'.format(self.get_time_stamp()),'wb') as obj:
            obj.write(b)

    def upload_statement(self,s_no):
        '''
        导出对账单
        '''
        url = self.url + '/statement/download'
        data = {'statementNo': s_no}
        c,b = self.do_get_stream(url,data)
        assert c == 200
        with open('../data/对账单_{}.pdf'.format(s_no),'wb') as obj:
            obj.write(b)

    def mno_trigger(self,s_time,s_p_type):
        '''
        从MOSI获取MNO对账单数据
        '''
        url = self.url + '/statement/trigger/mno'

    def platform_data(self,s_time,cp):
        '''
        从大数据获取平台对账数据
        '''
        url = self.url + '/statement/prepare/platformData'
        data = {'statementTime':s_time,'spId':cp}
        c,b = self.do_post(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':

    os.environ['ENV'] = 'DEV'
    os.environ['GATE'] = 'false'

    s = Statement()
    redis_util = RedisUtils()
    cp = 'CMCC'
    s_type = 'ORDER_STATEMENT'
    s_time = '20200401000000'
    s.platform_data(s_time,cp)
    # redis_util.get_set_value(key='bill:compare_set:third:CMCC:ORDER_STATEMENT:20200401000000:false')

    # s.upload_statement_diff(s_no='DZD20210519133028632368640')
    # s.upload_statement(s_no='DZD20210519133028632368640')
    # s.abandon_statement(s_no='DZD20210510090226206368640',reason='nothing')
    # s.query_base_info(key='statementStatus')
    # s.cp_file(file_path='../data/JD_OPEN PAY账单.xlsx', file_name='JD_OPEN导入账单.xlsx', sp='JD_OPEN', s_time='2020-11-01 00:00:00', s_type='PAY_STATEMENT', s_p_type='MONTH')
    # s.cp_file(file_path='../data/JD_OPEN_ORDER账单.xlsx', file_name='JD_OPEN导入账单.xlsx', sp='JD_OPEN', s_time='2020-10-01 00:00:00', s_type='ORDER_STATEMENT', s_p_type='MONTH')
    # s.fail_cp_upload(sp='XIMALAYA',s_time='2020-05-01 00:00:00',s_type='PAY_STATEMENT')
    # redis_util.get_list_value("bill:upload_fail:{}:20200501000000:ORDER_STATEMENT".format(cp))
    # redis_util.get_hash_value("bill:check_record_map:platform:JD_OPEN:ORDER_STATEMENT:20201001000000:true")
    # redis_util.get_set_value("bill:compare_set:platform:JD_OPEN:ORDER_STATEMENT:20201001000000:true")
    # maps = ['check_record_map','compare_check_map']
    # sets = ['check_set','compare_set']
    # for i in maps:
    #     third_dict = redis_util.get_hash_value(key='bill:{}:third:{}:{}:{}:false'.format(i,cp,s_type,s_time))
    #     big = 'bill:{}:platform:{}:{}:{}:false'.format(i,cp,s_type,s_time)
    #     redis_util.del_key(big)
    #     for k,v in third_dict.items():
    #         redis_util.set_hash_value(big_key=big,small_key=k,value=v)
    #
    # for i in sets:
    #     third_sets = redis_util.get_set_value(key='bill:{}:third:{}:{}:{}:false'.format(i,cp,s_type,s_time))
    #     key = 'bill:{}:platform:{}:{}:{}:false'.format(i,cp,s_type,s_time)
    #     redis_util.del_key(key)
    #     for i in third_sets:
    #         redis_util.write_set_value(key,i)

    # res = s.generate_statement(cp=cp,s_time='2020-04-24 14:00:00',percent_platform=25.5,s_p_type='MONTH',s_type=s_type)
    # s.statement_list(third_name='XIMALAYA',beginTime=None,statementStatus=None)
    # s_no = 'DZD20210514131001355385024'
    # index = 1
    # size = 50
    # items = s.item_list(s_no,page_no=index,page_size=size)
    # data = []
    # page = int(items['totalCount'] /size)
    # if page < 2:
    #     data=items['data']
    # else:
    #     for i in range(1,page+1):
    #         items = s.item_list(s_no,i,size)
    #         data.extend(items['data'])
    # print(data)
    # for i in data:
    #     if not i['checkPersonId']:
    #         s.item_check(s_no,s_c_no=i['statementCheckNo'],s_m_amount=s.f.pyint(),s_r_no=1,remarks=s.f.word())
    #         lk.prt('{}明细确认成功！'.format(i['statementCheckNo']))
    # s.confirm_statement(s_no)

    # s.upload_statement(s_no)