import json

from box.base import Base
import os


class MAOrder(Base):
    def __init__(self):
        super().__init__()
        self.gate = True
        if os.getenv('ENV') not in ('PROD','PERF'):
            self.env = 'UAT'
        self.payment_url = self.read_conf('ma_env.conf', self.env, 'base_url_hu') + '/mosc-payment'
        self.order_url = self.read_conf('ma_env.conf', self.env, 'base_url_hu') + '/mosc-order'

    def assert_msg(self, code, body):
        print(json.dumps(body,ensure_ascii=False,indent=4))
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

    def count(self,aid,**kwargs):
        '''
        查询订单数量
        '''
        url = self.order_url + '/internal/v2/order/count'
        data = {'aid':aid,**kwargs}
        c,b = self.do_get(url,data)
        self.assert_msg(c,b)


if __name__ == '__main__':
    os.environ['ENV'] = 'UAT'
    aid = '9353263'
    vin = 'LFVTESTMOSC000129'
    ma_order = MAOrder()
    status_list = ['PAID','PROCESSING','PAY_FAILED']
    # ma_order.count(aid,orderCategory='00',orderStatusList=status_list)
    # ma_order.create_order(aid,vin)
    # ma_order.refund(order_no='ma20210303162711260364544',aid='4614183')
    # ma_order.order_list(aid='9349831',status=['FINISHED'],category='00',begin=None,end=None)
    # ma_order.ma_contract_sign(channel='ALIPAY',service='03',operator='030003')
    # ma_order.ma_get_sign_result(channel='ALIPAY',service='03',operator='030003')
    # ma_order.ma_release_sign(channel='ALIPAY',service='03',operator='030003')
    # ma_order.apply_invoice(order_no='ma20210615083909326704512',i_channel='MNO',i_type='1',i_title='CMCC开票',tax='445678909876543',email='995939534@qq.com')
    # ma_order.get_order_detail(aid='9349824',order_no='ma20210413154730087774144')
    # ma_order.get_order_detail_by_ex(ex_order='1017383379447808')
    # ma_order.update_business(order_no='2020121606064500532768',status='AKSK',desc=ma_order.f.sentence())

    # ma_order.sync_order_pay(aid='9349641',order_no='20210112104548022143360',pay_order_no='1234',channel='WECHAT_PAY',
    #                         pay_amount=0.01,pay_time=ma_order.time_delta(),pay_status='SUCCESS',discountAmount=0.02,
    #                         pay_type='QR_CODE')
    # ma_order.get_qr_code('ma2021030911013915116384',channel='11100')
    # order_no = ma_order.create_goods_order(aid='4614183',goods_id='17',category='MUSIC_VIP',quantity=1,point=True,durationTimes=1,vin='LFVTESTMOSC000129')['data']
    # order_no = ma_order.create_goods_order(aid='15867227',goods_id='5d9821d6a1b24ecfa829ec3963fc20c0',category='MEDIA_FLOW',quantity=1,vin='LFV3A23C2L3121054')['data']
    ma_order.create_goods_order(aid='9355005',goods_id='1010500000113868',category='RADIO_VIP',quantity=1,vin='LFVSOP2TEST000075')

