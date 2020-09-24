from base import Base
import requests,json


class Login(Base):
    def __init__(self):
        super().__init__()
        self.header = {
            "Content-Type": "application/json; charset=utf-8",
            # "Accept-Encoding": "gzip, deflate",
            "Accept-Encoding": "json, deflate",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            "cpId": "MOJI"
        }

    def oss_login(self):
        key = self.get_check_key()
        data =  {'remember_me':'true','captcha':1234,'username':'yangzengxiang','password':'CIbDs0uM12~~~','checkKey':key}
        url = 'http://49.233.52.178:3000/ep/oss/oss/public/v1/sys/login'
        code,body = self.do_post(url,data)
        self.assert_msg(code,body)


    def get_check_key(self, url='http://49.233.52.178:3000/ep/oss/oss/public/v1/sys/getCheckCode'):
        header = self.header
        rsp = requests.get(url=url, headers=header, verify=False)
        jrsp = json.loads(rsp.text)
        return jrsp.get("result").get("key")

if __name__ == '__main__':
    l = Login()
    l.oss_login()