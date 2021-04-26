from box.base import Base
from box.lk_logger import lk
import os

lk.prt('导入 MA API 基类>>>>')

class MABase(Base):
    def __init__(self,aid,user,password,vin,token=True):
        super().__init__()
        self.aid = aid
        self.vin = vin
        self.gate = True
        if os.getenv('ENV') not in ('CLOUD','PERF'):
            self.env = 'UAT'
        if token:
            lk.prt('开始获取token...')
            self.add_header(self.read_conf('ma_env.conf',self.env,'token_host'),user,password,vin)

    def assert_msg(self,code,body):
        assert code == 200
        print(body)
        assert body['status'] == 'SUCCEED'


class MAOrder(Base):
    def __init__(self):
        super().__init__()
        self.gate = True
        self.payment_url = self.read_conf('ma_env.conf', self.env, 'pay_host')
        self.order_url = self.read_conf('ma_env.conf', self.env, 'order_host')

    def assert_msg(self, code, body):
        print(body)
        assert 200 == code
        assert body['status'] == 'SUCCEED'

    def generate_order_no(self):
        '''
        mosc-order内部生成订单号
        :return:
        '''
        url = self.order_url + '/internal/v2/order/generateOrderId'
        c,b = self.do_post(url,None)
        self.assert_bm_msg(c,b)
        return b['data']

    def create_order(self,aid,vin):
        '''
        mosc-order内部创建订单接口
        :return:
        '''
        info = self.f.pydict(value_types=str)
        # no = self.generate_order_no()
        ex = self.f.md5()
        cp = self.f.phone_number()
        data = {'orderCategory':'03',
                'spId':'180001',
                # 'orderNo':no,
                'aid':aid,
                'vin':vin,
                'vehModelCode':'川A389NG',
                'businessInfo':info,
                'serviceId':18,
                'orderType':'BUSINESS',
                'exOrderNo':ex,
                'cpOrderNo':cp,
                'title':'测试用例',
                'businessState':'业务状态',
                'businessStateDesc':'业务状态描述',
                'timeout':1,
                'amount':1.00,
                'payAmount':0.01,
                'discountAmount':0.99}
        url = self.order_url + '/internal/v2/order/create'
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)

    def refund(self,order_no,aid):
        '''
        mosc-order内部发起退款接口
        :param order_no:
        :return:
        '''
        url = self.order_url + '/internal/v2/order/refund'
        data = {'aid':aid,'orderNo':order_no,'reason':'测试退款','refundType':'BUSINESS'}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)

    def order_list(self,aid,status:list,category,begin,end):
        '''
        内部接口:获取订单列表
        :param aid:
        :param status:
        :param category:
        :param begin:
        :param end:
        :return:
        '''
        url = self.order_url + '/internal/v2/order/list'
        data = {'aid':aid,'orderStatusList':status,'orderCategory':category,'beginTime':begin,'endTime':end}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)



    def get_order_detail(self, aid,order_no):
        url = self.order_url + '/internal/v2/order/detail'
        data = {'aid':aid,'orderNo':order_no}
        c, b = self.do_get(url, data)
        self.assert_bm_msg(c,b)

    def get_order_detail_by_ex(self, ex_order):
        '''
        根据外部订单号查询订单详情
        :param ex_order:
        :return:
        '''
        url = self.order_url + '/internal/v2/order/getDetailByExOrderNo'
        data = {'exOrderNo':ex_order}
        c, b = self.do_get(url, data)
        self.assert_bm_msg(c,b)

    def get_goods_list(self):
        pass

    def create_goods_order(self, goods_id, category, aid, quantity,vin, point=False, **kwargs):
        '''
        mosc-order底层创建商品订单接口
        :param goods_id:
        :param category:
        :param aid:
        :param quantity:
        :param point:
        :param kwargs:
        :return:
        '''
        url = self.order_url + '/internal/v2/goods/creatOrder'
        data = {'aid': aid, 'goodsId': goods_id, 'vin': vin,
                'orderCategory': category, 'quantity': quantity, 'usedPoint': point, **kwargs}
        c, b = self.do_post(url, data)
        self.assert_bm_msg(c,b)
        return b

    def get_ma_qr_code(self, order_no, pay_type):
        '''
        MA订单获取支付二维码
        :param aid: 用户id
        :param order_no: 订单号
        :param pay_type: 支付类型11100支付宝普通支付11103支付宝支付并签约12100,12103
        :return:
        '''
        url = self.payment_url + '/api/v2/vins/{}/users/{}/orders/{}/payments/qrCode'.format(self.vin, self.aid,
                                                                                                  order_no)
        data = {'payType': pay_type}
        c, b = self.do_get(url, data)
        print(b)
        assert c == 200

    def ma_release_sign(self,aid,vin,channel,service,operator):
        '''
        MA免密解约
        :param channel:签约渠道WXPAY,ALPAY
        :param service: 业务，目前支持GAS,03
        :param operator: CP，目前支持JDO,030003
        :return:
        '''
        url = self.payment_url + '/internal/v2/app/contract/unsign'
        data = {'operatorId': operator, 'payChannel': channel, 'serviceId': service}
        c, b = self.do_post(url, data)
        self.assert_bm_msg(c, b)
        return b

    def apply_invoice(self,order_no,i_channel,i_type,i_title,tax,email,**kwargs):
        '''
        mosc-order申请开票api
        :param order_no: MS订单号
        :param i_channel:
        :param i_type:
        :param i_title:
        :param tax:
        :param email:
        :param kwargs:
        :return:
        '''
        url = self.order_url + '/internal/invoice/v1/apply'
        data = {'orderNo':order_no,'invoiceChannel':i_channel,'invoiceType':i_type,'invoiceTitle':i_title,'taxNumber':tax
                ,'email':email,**kwargs}
        c,b = self.do_post(url,data)
        self.assert_bm_msg(c,b)

    def get_VWlist(self,beginTime,endTime,orderStatus,pagelndex,pageSize,**kwargs):
        url = 'http://192.168.133.156:30994/vwlink/hu/mobile/order/v1/orders/list'
        data = {'beginTime': beginTime,'endTime':endTime,'orderStatus':orderStatus,'pagelndex':pagelndex,'pageSize': pageSize, **kwargs}
        c,b = self.do_get(url,data)
        self.assert_bm_msg(c,b)


    def cancel(self,order_no,aid):
        '''
        内部取消订单接口
        :param order_no:
        :param aid:
        :return:
        '''
        url = self.order_url + '/internal/v2/order/cancel'
        data = {'orderNo':order_no,'aid':aid}
        c,b = self.do_get(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':
    os.environ['ENV'] = 'UAT'
    aid = '4614233'
    vin = 'LFVTESTMOSC000129'
    ma_order = MAOrder()
    # ma_order.create_order(aid,vin)
    # ma_order.refund(order_no='ma20210303162711260364544',aid='4614183')
    # music_order.order_list(music_order.aid,status=['FINISHED'],category='01',begin=None,end=None)
    # ma_order.ma_contract_sign(channel='ALIPAY',service='03',operator='030003')
    # ma_order.ma_get_sign_result(channel='ALIPAY',service='03',operator='030003')
    # ma_order.ma_release_sign(channel='ALIPAY',service='03',operator='030003')
    # ma_order.apply_invoice(order_no='ma20210224155318454245760',i_channel='JDO',i_type='1',i_title='极豆科技',tax='445678909876543',email='995939534@qq.com')
    # ma_order.get_order_detail(aid='9349824',order_no='ma20210413154730087774144')
    # ma_order.get_order_detail_by_ex(ex_order='1017383379447808')
    # ma_order.update_business(order_no='2020121606064500532768',status='AKSK',desc=ma_order.f.sentence())

    # ma_order.sync_order_pay(aid='9349641',order_no='20210112104548022143360',pay_order_no='1234',channel='WECHAT_PAY',
    #                         pay_amount=0.01,pay_time=ma_order.time_delta(),pay_status='SUCCESS',discountAmount=0.02,
    #                         pay_type='QR_CODE')
    # ma_order.get_qr_code('ma2021030911013915116384',channel='11100')
    # ma_order.alipay_callback()
    # order_no = ma_order.create_goods_order(aid='4614183',goods_id='17',category='MUSIC_VIP',quantity=1,point=False,durationTimes=1,vin='LFVTESTMOSC000129')['data']
    order_no = ma_order.create_goods_order(aid=aid,goods_id='cc50badd5bd6418b9c431f87394640fe',category='WIFI_FLOW',quantity=1,vin=vin)['data']
    # ma_order.create_goods_order(aid='9349863',goods_id='1010500100000535429',category='RADIO_VIP',quantity=1,vin='LFVSOP2TEST000080')
    # ma_order.get_ma_qr_code(order_no='ma20210419141205531225280',pay_type='11100')

