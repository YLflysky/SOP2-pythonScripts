import requests
import time
import uuid
from urllib import parse
import hashlib
import json
import pymysql
import configparser
import xlrd
from box.lk_logger import lk
import os
import datetime
from box.db import MysqlConfig
from faker import Faker
from kafka import KafkaProducer
from kafka.errors import KafkaError
import sys

class Base:

    def __init__(self):
        self.env = os.getenv('ENV')
        self.header = {}
        self.header['Content-type'] = 'application/json; charset=utf-8'
        self.f = Faker(locale='zh-CN')

        try:
            if os.getenv('GATE') == 'true':
                self.header['x-namespace-code'] = 'cdp-uat-default'
                self.header['x-microservice-name'] = 'api-gateway'
                self.header['Did'] = 'VW_HU_BS43C4_EPTest_Android9.0_v1.2.0'
                self.header['userModel'] = 'DEFAULT'
                self.gate = True
            else:
                self.gate = False
        except Exception as e:
            lk.prt('init error:{}'.format(e))
            return


    public_param = {
        #  "appId": "666666",
        # "os": "android",
        "packageName": "com.faw-vw.hu",
        "userModel": "DEFAULT",

    }

    def get_time_stamp(self,days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        """获取时间戳

            - :return:返回时间戳
            """
        temp_time = self.time_delta(days,seconds,microseconds,milliseconds,minutes,hours,weeks)
        time_array = time.strptime(temp_time,'%Y-%m-%d %H:%M:%S')
        time_stamp = str(int(time.mktime(time_array))*1000)
        return time_stamp

    def _sign_time(self):

        temp = time.time()*1000
        return str(int(temp))

    def rand_uuid(self):
        """随机产生一个32位的uuid
        - :return: 返回uuid
        """
        temp = str(uuid.uuid1())
        return temp.replace("-", "")

    def _url_encode(self, uri: dict):
        params = []
        for key, value in uri.items():
            value = parse.quote(value)
            params.append('{}={}'.format(key, value))
        return '&'.join(params)

    def _calc_digital_sign(self, url, params):
        """计算签名

        - :param uri: 【必填】带计算前面的uri, 类型：string
        - :return: 返回附加的url
        """
        if params is None:
            params = {}
        # 生成时间戳和nonce
        sign_timestamp = str(int(time.time() * 1000))
        temp = str(uuid.uuid1())
        nonce = temp.replace("-", "")

        # 1.获取资源路径
        resource_uri = url.replace("https://otherbackend-uat-sop2.mosc.faw-vw.com/test-access/tm/", "")
        resource_uri = resource_uri.replace("https://hu-uat-sop2.mosc.faw-vw.com/test-access/tm/", "")
        resource_uri = resource_uri.replace("https://h5-uat-sop2.mosc.faw-vw.com/test-acce/tm/ss","")
        #resource_uri ="mos/dealer-maintenance/oapi/updateMaintenanceOrder"

        # 2.获取查询参数
        url_query_dict=params
        # 3.添加签名时间，排序
        url_query_dict["appkey"] = "3717440806"
        url_query_dict["signt"] = sign_timestamp
        url_query_dict["nonce"] = nonce
        url_query_dict["userModel"] = "DEFAULT"
        url_query_dict["os"] = "android"
        # 排序并生成字符串
        key_sort = sorted(url_query_dict.keys())

        # 4.拼接
        parm_list = []
        for key in key_sort:
            temp = key + '=' + str(url_query_dict[key])
            parm_list.append(temp)

        catent = "_".join(parm_list)
        # 5.添加应用资源和secret_key
        last_url_encode = resource_uri + "_" + catent + "_" + "b9784ddc19aa9ec47d2dfa1dfbca7934"

        # 计算MD5
        last_url_encode = parse.quote(last_url_encode.encode(), safe='')
        my_md5 = hashlib.md5()
        my_md5.update(last_url_encode.encode())
        digital_sign = my_md5.hexdigest()
        url_query_dict["sign"] = digital_sign
        return url_query_dict

    def get_pro_path(self):
        if 'win' in sys.platform:
            seperator = '\\'
        else:
            seperator = '/'
        current_path = os.path.abspath(os.path.dirname(__file__))
        pro_name = 'SOP2-pythonScripts'
        pro_path = current_path[:current_path.find(pro_name + seperator) + len(pro_name + seperator)]
        return pro_path

    def get_token(self,other='MA',username='18224077254',password='123456',vin='LFV3A23C1K3161804'):
        if other=='MA':
            url = "https://otherbackend-uat-sop2.mosc.faw-vw.com/test-access/tm/user/api/v1/token"
        elif other=='BM':
            url = 'http://49.233.242.137:18031/sop2bm/hu/cm/user/api/v1/token'
        headers = {
            'Content-Type': 'application/json',
            'TraceId': 'app-store#recommend-list#1527758664#X9G-11111.04.2099990054#12345678',
            'Did': 'VW_HU_CNS3_X9G-11111.04.2099990054_v3.0.1_v0.0.1'}

        payload = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "client_id": "X9G-11111.04.2099990054",
            "response_type": "token id_token",
            "scope": "openid",
            "login_type": "HU",
            "vin": vin
        }
        data = json.dumps(payload)

        try:
            response = requests.post(url=url, data=data, headers=headers, verify=False)

            assert response.status_code == 200
            content = json.loads(response.content)
            token_type = content['data']['token_type']
            access_token = content['data']['access_token']
            return token_type + " " + access_token
        except Exception as e:
            raise Exception("Get token failed: {}".format(e))

    def _is_json(self, string):
        try:
            json_str = json.loads(string)
        except Exception:
            return False
        return True

    def do_post(self, url, data,params=None,**kwargs):
        if self.gate:
            params = self._calc_digital_sign(url,params)
        lk.prt('final post url is:{}'.format(url))
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        print(type(data), data)
        if data is not None:
            data = data.encode('utf-8')
        lk.prt('final post header is:{}'.format(self.header))
        res = requests.post(url=url, data=data,params=params, headers=self.header, verify=False,**kwargs)
        try:
            response_body = json.loads(res.text)
        except Exception as e:
            lk.prt('解析json字符串出错:',e)
            lk.prt(res.text)
        else:
            return res.status_code, response_body

    def do_post_file(self,url,params,data,file_path):
        '''
        上传文件接口测试
        :param url:
        :param file_path:
        :return:
        '''
        if self.gate:
            params = self._calc_digital_sign(url,params)
        lk.prt('final post url is:{}'.format(url))
        if isinstance(data, dict):
            data = json.dumps(data, ensure_ascii=False)
        print(type(data), data)
        if data is not None:
            data = data.encode('utf-8')

        del self.header['Content-type']
        lk.prt('final post header is:{}'.format(self.header))
        f = open(file_path,'rb')
        files = {'file':f}
        res = requests.post(url=url,params=params, data=data, headers=self.header,files=files, verify=False)
        f.close()
        response_body = json.loads(res.text)
        self.header['Content-type'] = 'application/json; charset=utf-8'
        return res.status_code, response_body

    def do_put(self, url,params, data):
        if self.gate:
            params = self._calc_digital_sign(url,params)
        else:
            self.header = {'Content-Type': 'application/json'}
        lk.prt('final put url is:{}'.format(url))
        if isinstance(data, dict):
            data = json.dumps(data)
        lk.prt('final put data is:{}'.format(data))
        lk.prt('final put header is:{}'.format(self.header))
        res = requests.put(url=url,params=params, data=data, headers=self.header, verify=False)
        response_body = json.loads(res.text)
        return res.status_code, response_body

    def do_get(self, url, params):
        if self.gate:
            params = self._calc_digital_sign(url, params)
        lk.prt('final get url is:{}'.format(url))
        lk.prt('final get header is:{}'.format(self.header))
        lk.prt('final get param is:{}'.format(params))
        try:
            res = requests.get(url=url,params=params, headers=self.header, verify=False)
            response_body = json.loads(res.text)
            return res.status_code, response_body
        except Exception as e:
            lk.prt(e)

    def do_delete(self, url, params):
        params = self._calc_digital_sign(url, params)
        lk.prt('final delete url is:{}'.format(url))
        try:
            res = requests.delete(url=url,params=params, headers=self.header, verify=False)
            response_body = json.loads(res.text)
            return res.status_code, response_body
        except Exception as e:
            lk.prt(e)

    def do_mysql_select(self, msg, db,host='EP'):
        config_dict = eval('MysqlConfig.{}_{}.value'.format(host,self.env))
        conn = pymysql.connect(database=db,
                               host=config_dict['host'],
                               port=config_dict['port'],
                               user=config_dict['username'],
                               password=config_dict['password'])
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute(msg)
        res = cur.fetchall()
        lk.prt('执行sql语句成功:{}'.format(msg))
        for res1 in res:
            for key,val in res1.items():
                if isinstance(val,datetime.datetime):
                    res1[key]=self.str_time(val)

        cur.close()
        conn.close()
        return res

    def do_mysql_exec(self,msg, db,host='EP'):
        config_dict = eval('MysqlConfig.{}_{}.value'.format(host, self.env))
        conn = pymysql.connect(database=db,
                               host=config_dict['host'],
                               port=config_dict['port'],
                               user=config_dict['username'],
                               password=config_dict['password'])
        cur = conn.cursor(pymysql.cursors.DictCursor)
        try:
            # 执行sql语句
            cur.execute(msg)
            # 提交修改
            conn.commit()
            lk.prt('执行sql语句成功:{}'.format(msg))
        except Exception as e:
            lk.prt('执行失败：{}'.format(e))
            conn.rollback()

        finally:
            cur.close()
            conn.close()



    def read_conf(self, name, section, option):
        '''
        read config files
        :param name:file name
        :param section: config section such as [...]
        :param option: option in one section
        :return: the value of the chosen option
        '''
        config = configparser.ConfigParser()
        conf_path = os.path.join(self.get_pro_path(),'conf/{}'.format(name))
        lk.prt('config path is:{}'.format(conf_path))
        config.read(conf_path)
        return config.get(section, option)

    def read_excel_dict(self, file_path, sheet_name):

        # 读取excel文件路径
        wb = xlrd.open_workbook(file_path)
        # 获取工作表
        sheet = wb.sheet_by_name(sheet_name)
        # 获取数据行数
        rows = sheet.nrows
        data_list = []
        for i in range(1, rows):
            row_data = sheet.row_values(i)
            data_dict = {}
            for index, key in enumerate(sheet.row_values(0)):
                data = row_data[index]
                if data == '':
                    data_dict[key] = None
                elif isinstance(data, float) and data == int(data):
                    data_dict[key] = str(int(data))
                else:
                    data_dict[key] = data
            data_list.append(data_dict)
        return data_list

    def time_delta(self, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        """在当前时间基础上进行时间增减操作

        - :param days:  【可选】单位：天；类型：整数
        - :param seconds: 【可选】单位：秒；类型：整数
        - :param microseconds: 【可选】单位：毫秒；类型：整数
        - :param milliseconds: 【可选】单位：千毫秒；类型：整数
        - :param minutes:【可选】单位：分钟；类型：整数
        - :param hours:【可选】单位：小时；类型：整数
        - :param weeks:【可选】单位：周；类型：整数
        - :return: 返回格式化后的时间

        - 举例：
        | Time Delta | days=5 |
        """
        # 获取当前时间
        now = datetime.datetime.now()
        # 当前时间加上半小时
        add_time = now + datetime.timedelta(days=days, seconds=seconds, microseconds=microseconds,
                                            milliseconds=milliseconds,
                                            minutes=minutes, hours=hours, weeks=weeks)
        # 格式化字符串输出
        formatted_time = add_time.strftime('%Y-%m-%d %H:%M:%S')
        return formatted_time

    def assert_msg(self,code,body):
        print(body)
        assert 200 == code
        assert 'SUCCEED' == body['returnStatus']

    def str_time(self,data_time:datetime.datetime):
        temp = data_time.strftime('%Y-%m-%d %H:%M:%S')
        return temp

    def stamp_to_str(self,stamp):
        time_array = time.localtime(int(stamp)/1000)
        return time.strftime('%Y-%m-%d %H:%M:%S',time_array)

    def send_kafka_msg(self,host,topic,data):
        '''
        模拟发送kafka消息
        :param host: kafka ip地址
        :param topic:
        :param data: 发送的消息
        :return:
        '''

        producer = KafkaProducer(bootstrap_servers=host,api_version=(0,10),retries=5)

        msg = bytes(json.dumps(data),encoding='utf-8')
        print(msg)
        try:
            future = producer.send(topic, msg)
            future.get()
            print('send message succeed.')
        except KafkaError as e:
            print('send message failed. [e] ={}'.format(e))


