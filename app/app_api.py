from box.base import Base
from box.lk_logger import lk
import os


class App(Base):
    '''
    ftb2.2提供给oneApp的接口
    '''
    def __init__(self,name,password,aid):
        super().__init__()
        # APP网关需要验签和token
        self.gate = True
        self.name = name
        self.password = password
        self.uid = aid
        # self.header['aid']='9353507'
        self.mobile_url = self.read_conf('sop2_env.conf', self.env, 'one_app_host')
        self.hu_url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
        self.device_id = 'VW_HU_CNS3_GRO-63301.10.23242312_v1.0.1_v0.0.1'
        lk.prt('开始获取token...')
        self.cdp_url = self.read_conf('sop2_env.conf', self.env, 'cdp_host')
        token_url = self.cdp_url + '/user/public/v1/login'
        apptoken=self.header['Authorization'] = self.get_token(token_url, self.name, self.password,vin=None,client='APP')
        print(apptoken)
        self.header['Did'] = self.device_id
        # self.header['vin']  = 'LFVSOP2TEST000353'

        #前端创建的参数
        # self.header['traceid'] = 'a8abb4bb284b5b27aa7cb790dc20f80b'
        # self.header['x-forwarded-proto'] = 'https,http'
        # self.header['content-length'] = '183'
        # self.header['x-forwarded-proto'] = 'zh-Hans;q=1'
        # self.header['x-forwarded-port'] = '80'
        # self.header['x-forwarded-for'] = '222.209.200.157,172.29.2.1'
        # self.header['forwarded'] = 'proto=http;host=mobile-cs-uat.mosc.faw-vw.com;for=\"172.29.2.1:20981\"'
        # self.header['user-agent'] = 'NewAfterMarket-ios/87 (iPhone; iOS 14.2; Scale/2.00)'
        # self.header['x-client-proto'] = 'https'
        # self.header['Did'] = ''
        # self.header['Did'] = ''
        # self.header['Did'] = ''
        # self.header['Did'] = ''
        # self.header['Did'] = ''
        # self.header['Did'] = ''
        # self.header['Did'] = ''
        # self.header['Did'] = ''



    def calendar_mobile_sync(self,current_time,vin,events:list):
        '''
        APP同步用户日历事件
        :param current_time: long类型时间戳
        :param events: 事件，列表类型
        :return:
        '''
        self.header['vin'] = vin
        url = self.mobile_url + '/oneapp/calendar/public/event/sync'
        data = {'currentTime':current_time,'events':events}
        c,b = self.do_post(url,data,gateway='APP')
        print(b)
        assert c == 200
        return b

    def calendar_mobile_find_all(self,vin):
        '''
        app获取用户所有事件接口
        :return:
        '''
        self.header['vin'] = vin
        url = self.mobile_url + '/oneapp/calendar/public/event/findAll'
        code,body = self.do_get(url,None,gateway='APP')
        print(body)
        assert code == 200
        return body

    def get_tenant_by_vin(self,vin):
        '''
        根据vin码获取到是哪个项目的车型
        :return:
        '''
        url = self.hu_url + '/vs/ftb-vehicle/public/v1/tenant/get_by_vin'
        data = {'vin':vin}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)
        return b['data']['tenantId']

    def create_app_order(self,vin,goodsId,orderCategory,userId,usedPoint,priceType,count):
        url=  self.mobile_url+'/oneapp/order/v1/create'
        # url ='http://49.233.242.137:18020' + '/order/v1/create'
        data ={'goodsId':goodsId,'orderCategory':orderCategory,"priceType":priceType,"usedPoint":usedPoint,"userId":userId,"durationTimes":"11",'count':count}
        # data = {"vin":"LFVSOP2TEST000353","goodsId":"1010500100000535429","orderCategory":"RADIO_VIP","priceType":"1","usedPoint":'true',"quantity":'1',"userId":"9350041","durationTimes":"11"}
        code,body = self.do_post(url,data,gateway='APP')
        self.header['vin'] = vin
        print(body)
        return body

    def cancel_order(self,orderNo):
        url=self.mobile_url+'/oneapp/order/v1/cancel'
        data = {'orderNo': orderNo}
        code,body = self.do_post(url,data,gateway='APP')
        print(body)
        return body



    def get_app_list(self,orderStatus,orderCategoryList,tenantIdList): #获取列表
        url =self.mobile_url+'/oneapp/order/v1/list'
        # url = 'http://192.168.137.1:18030/oneapp/order/v1/list'
        # url='http://49.233.242.137:18020/oneapp/order/v1/list'
        # url ='http://192.168.137.1:8230' + '/order/v1/create'
        data = {'orderStatus': orderStatus,'orderCategoryList':orderCategoryList,"tenantIdList": tenantIdList}
        # data = {"vin":"LFVSOP2TEST000353","goodsId":"1010500100000535429","orderCategory":"RADIO_VIP","priceType":"1","usedPoint":'true',"quantity":'1',"userId":"9350041","durationTimes":"11"}
        code, body = self.do_post(url, data, gateway='APP')
        print(body)
        return body

    def getneworder(self):
        # url = 'https://mobile-cs-uat.mosc.faw-vw.com/mos/payment/api/v1/createOrder'
        url=self.mobile_url+'/mos/app/public/findOrderDetial'
        data=None
        code, body = self.do_get(url, data, gateway='APP')
        print(body)
        return body

    def get_app_detail(self,orderNo): #获取列表
        url =self.mobile_url+'/oneapp/order/v1/detail'
        # url='http://49.233.242.137:18020/oneapp/order/v1/detail'
        # url ='http://192.168.137.1:8230' + '/order/v1/create'
        data = {'orderNo': orderNo}
        # data = {"vin":"LFVSOP2TEST000353","goodsId":"1010500100000535429","orderCategory":"RADIO_VIP","priceType":"1","usedPoint":'true',"quantity":'1',"userId":"9350041","durationTimes":"11"}
        code, body = self.do_get(url, data, gateway='APP')
        print(body)
        return body

    def get_app_delete1(self,orderNo): #获取详情
        url =self.mobile_url+'/oneapp/order/v1/delete'
        # url='http://49.233.242.137:18020/oneapp/order/v1/delete'
        # url ='http://192.168.137.1:8230' + '/order/v1/create'
        data = {'orderNo': orderNo}
        # data = {"vin":"LFVSOP2TEST000353","goodsId":"1010500100000535429","orderCategory":"RADIO_VIP","priceType":"1","usedPoint":'true',"quantity":'1',"userId":"9350041","durationTimes":"11"}
        code, body = self.do_post(url, data,gateway='APP')
        print(body)
        return body

    def get_app_cancel(self,orderNo):
        url =self.mobile_url+'/oneapp/order/v1/cancel'
        # url='http://49.233.242.137:18020/oneapp/order/v1/delete'
        # url ='http://192.168.137.1:8230' + '/order/v1/create'
        data = {'orderNo': orderNo}
        # data = {"vin":"LFVSOP2TEST000353","goodsId":"1010500100000535429","orderCategory":"RADIO_VIP","priceType":"1","usedPoint":'true',"quantity":'1',"userId":"9350041","durationTimes":"11"}
        code, body = self.do_post(url, data,gateway='APP')
        print(body)
        return body
    def get_passfreequery(self,signPay,vin,cpSeller):
        #获取签约状态
        url = self.mobile_url+'/oneapp/pay/v1/agreement/passfree/query'
        # url='http://49.233.242.137:18020/oneapp/pay/v1/agreement/passfree/query'
        # url ='http://192.168.137.1:8230' + '/order/v1/create'
        data = {'signPay': signPay,'vin':vin,'cpSeller':cpSeller}
        # data = {"vin":"LFVSOP2TEST000353","goodsId":"1010500100000535429","orderCategory":"RADIO_VIP","priceType":"1","usedPoint":'true',"quantity":'1',"userId":"9350041","durationTimes":"11"}
        code, body = self.do_post(url, data, gateway='APP')
        print(body)
        return body

    def get_passfreesign(self,signPay,vin,cpSeller,displayAccount):
        #获取签约状态
        url = self.mobile_url+'/oneapp/pay/v1/agreement/passfree/sign'
        # url='http://49.233.242.137:18020/oneapp/pay/v1/agreement/passfree/sign'
        # url ='http://192.168.137.1:8230' + '/order/v1/create'
        data = {'signPay': signPay,'vin':vin,'cpSeller':cpSeller,'displayAccount':displayAccount}
        # data = {"vin":"LFVSOP2TEST000353","goodsId":"1010500100000535429","orderCategory":"RADIO_VIP","priceType":"1","usedPoint":'true',"quantity":'1',"userId":"9350041","durationTimes":"11"}
        code, body = self.do_post(url, data, gateway='APP')
        print(body)
        return body

    def get_passfreecloseSign(self,signPay,vin,cpSeller):
        #获取签约状态
        url = self.mobile_url+'/oneapp/pay/v1/agreement/passfree/closeSign'
        # url='http://49.233.242.137:18020/oneapp/pay/v1/agreement/passfree/closeSign'
        # url ='http://192.168.137.1:8230' + '/order/v1/create'
        data = {'signPay': signPay,'vin':vin,'cpSeller':cpSeller}
        # data = {"vin":"LFVSOP2TEST000353","goodsId":"1010500100000535429","orderCategory":"RADIO_VIP","priceType":"1","usedPoint":'true',"quantity":'1',"userId":"9350041","durationTimes":"11"}
        code, body = self.do_post(url, data, gateway='APP')
        print(body)
        return body



    def free_access_pay(self,aid,vin,channel,order_no):
        '''
        免密支付接口
        :param vin:
        :param channel:
        :param order_no:
        :return:
        '''
        self.header['vin'] = vin
        self.header['aid'] = aid
        url = self.mobile_url + '/oneapp/pay/v1/signPay'
        data = {'payChannel':channel,'orderNo':order_no}
        code,body = self.do_post(url,data,gateway='APP')
        print(body)
        assert code == 200
        return body['data']



    def get_invoiceapply(self, orderNo, invoiceChannel, invoiceType,invoiceTitle,taxNumber,accountsBank
                     ,bankNumber,mobile,mailingAddress,email,remark,address):
    # 申请开票
        url = self.mobile_url + '/oneapp/invoice/v1/apply'
    # url='http://49.233.242.137:18020/oneapp/pay/v1/agreement/passfree/closeSign'
    # url ='http://192.168.137.1:8230' + '/order/v1/create'
        data = {'orderNo':orderNo,'invoiceChannel':invoiceChannel, 'invoiceType':invoiceType,'invoiceTitle':invoiceTitle,
            'taxNumber':taxNumber,'accountsBank':'中国银行','bankNumber':'中国银行','mobile':'18502587652',
            'mailingAddress':'34873uei@qw.com','email':'7334343@qq.com','remark':'无','address':'一汽大众'}
    # data = {"vin":"LFVSOP2TEST000353","goodsId":"1010500100000535429","orderCategory":"RADIO_VIP","priceType":"1","usedPoint":'true',"quantity":'1',"userId":"9350041","durationTimes":"11"}
        code, body = self.do_post(url, data, gateway='APP')
        print(body)
        return body


if __name__ == '__main__':

    os.environ['ENV'] = 'UAT'
    app = App(name='13353116625',password='000000',aid='9353507')

    # app.get_tenant_by_vin(vin='LFVSOP2TESTLY0002')
    # app.get_passfreequery(signPay='WXPAY',vin='LFVSOP2TEST000353',cpSeller='CMCC') #获取签约状态
    # app.get_passfreesign(signPay='ALPAY',vin='LFVSOP2TEST000353',cpSeller='BM',displayAccount='112')#免密签约
    # app.get_passfreecloseSign(signPay='WXPAY',vin='LFVSOP2TEST000353',cpSeller='BM')#取消免密签约

    # event = {'localEventId': app.f.pyint(100, 1000), 'cudStatus': 'C','rrule':'Only Once',
    #                  'eventStartTime': app.get_time_stamp(days=-1), 'eventEndTime': app.get_time_stamp(days=1)}
    # app.calendar_mobile_sync(current_time=None,events=[event],vin='LFVSOP2TESTLY0003')
    # app.calendar_mobile_find_all('LFVSOP2TESTLY0002')
    # app.free_access_pay(aid='9353497',vin='LFVSOP2TESTLY0002',channel='WXPAY',order_no='20210201172351827405504')
    # app.get_app_list(orderStatus='FINISH',orderCategoryList=None,tenantIdList=None)
    # app.get_app_detail(orderNo='ma20210203155156373274432')
    # app.create_app_order(vin='LFVSOP2TESTLY0003',goodsId='1010500000113868',orderCategory='RADIO_VIP',userId='9353507',
    # usedPoint='true', priceType='1',count='1')
    # app.create_app_order(vin='LFVSOP2TESTLY0003', goodsId='253', orderCategory='WIFI_FLOW',
    #                      userId='49987',
    #                      usedPoint='true', priceType='1', count='1')
    # app.create_app_order(vin='LFVTEST1231231231', goodsId='17', orderCategory='MUSIC_VIP',
    #  userId='9350041', usedPoint='true', priceType='4', count='1')
    # app.cancel_order(orderNo='ftb20210207170546393483328')
    # app.get_app_delete1(orderNo='ma20210203155246134106496')
    # app.get_app_cancel(orderNo='ma20210224164756151245760')
    app.get_invoiceapply(orderNo="ftb20210315163037464913408",invoiceChannel='CMCC', invoiceType='1',invoiceTitle='一汽大众',
            taxNumber='334565443rt',accountsBank='中国银行',bankNumber='87778877',mobile='185267367621',
            mailingAddress='34873uei@qw.com',email='7334343@qq.com',remark='无',address='龙泉')
    # app.getneworder()