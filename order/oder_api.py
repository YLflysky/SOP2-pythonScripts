from box.base import Base
import random
import os
import json


class Order(Base):

    def __init__(self):
        super().__init__()
        if self.gate:
            self.header['Authorization'] = self.get_token(other='BM')

        self.url = self.read_conf('sop2_env.conf', self.env, 'be_host')

    def update_order(self,order_no,aid,**kwargs):
        '''
        底层修改订单服务
        '''
        url = self.url + '/sm/order/v1/order/update'
        data = {'orderNo': order_no, 'aid': aid,**kwargs}
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)

    def add_order(self):
        '''
        底层添加订单服务
        '''
        url = self.url + '/sm/order/v1/order'
        num = random.randint(10000000000000000000, 99999999999999999999)
        businessInfo = {'productId': 'code_002', 'price': 111, 'quantity': 1}
        data = {'orderCategory': '110', 'spId': 'KUWO', 'aid': '9349643',
                'vehModelCode': '040804', 'businessInfo': businessInfo, 'vin': 'LFVSOP2TEST000018', 'serviceId': 'MUSIC',
                'orderType': 'BUSINESS', 'cpOrderNo': 'MA{}'.format(num), 'title': self.f.sentence(),
                'businessState': 'PROCESSING', 'businessStateDesc': 'SUCCESS', 'amount': 1, 'payAmount': 1,
                'timeout': 30, 'discountAmount': 1,'status':'WAITING_PAY'}
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)
        return body['data']

    def del_order(self,order_no,aid):
        url = self.url + '/sm/order/v1/order/delete'
        data = {'orderNo':order_no,'aid':aid}
        code,body = self.do_get(url,data)
        assert 200 == code
        print(body)
        return body

    def invoice_detail(self, aid, invoice_no):
        '''
        获取发票详情
        :param invoice_no:发票编号，唯一索引
        :param aid:用户id，用于header中

        :return:
        '''

        url = self.url + '/sm/order/v1/invoice/detail'
        self.header['aid'] = aid
        data = {'invoiceNo': invoice_no}
        code, body = self.do_get(url, data)
        print(code,body)
        return body

    def sync_order(self,ex,origin,aid,category,**kwargs):
        '''
        同步订单接口
        '''
        url = self.url + '/sm/order/v1/order/sync'
        data = {'exOrderNo':ex,'origin':origin,'aid':aid,'orderCategory':category,**kwargs}

        code,body = self.do_post(url,data)
        self.assert_msg(code,body)
        return body

    def order_detail(self, aid, order_no):
        url = self.url + '/sm/order/v1/order/orderNo/{}'.format(order_no)
        code, body = self.do_get(url, params={'aid': aid})
        self.assert_msg(code, body)

    def sync_invoice(self, invoiceNo, status, party,orderNo:list):
        '''
        底层同步发票信息api
        '''
        url = self.url + '/sm/order/v1/invoice/notify/ep/sync'

        data = {'actionId': 'INVOICE_UPDATE', 'aid': '123456', 'domainId': 'COMMON', 'epInvoiceId': '1',
                'epOrderIds': orderNo,
                'cpId': 'XIAOMA', 'invoiceNo': invoiceNo, 'partyType': party,
                'bankAccount': self.f.credit_card_number(), 'status': status,
                'remark': self.f.sentence(), 'price': self.f.pyint(), 'createTime': self.time_delta(days=-1),
                'transmissionTime': self.time_delta()}
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)

    def sync_invoice_total(self, data):
        url = self.url + '/sm/order/v1/invoice/notify/ep/sync'
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)

    def teardown_sync_invoice(self, orders:list, invoice):
        '''
        删除同步发票后的测试数据
        '''
        print('-----开始teardown------')
        self.do_mysql_exec('delete from order_invoice where invoice_no="{}"'.format(invoice), 'fawvw_order')
        for order in orders:
            self.do_mysql_exec(
                'delete from order_invoice_relation where order_id=(select id from `order` where ex_order_no="{}")'.format(
                    order), 'fawvw_order')
        print('同步的发票删除成功')

    def generate_order_no(self):
        url = self.url + '/sm/order/v1/order/genOrderNo'
        code, body = self.do_get(url, None)
        print(body)
        assert 200 == code
        return body


    def sync_order_kafka(self, ep_order_id, business_info: dict, domain='GAS', cp='NX_ENGINE'):
        '''
        从EP通过callback同步订单
        :param ep_order_id: ep订单编号
        :param business_info: 业务信息
        :param domain: 业务域
        :param cp: 供应商
        :return:
        '''
        header = {'domainId': domain}
        aid = self.f.pyint()
        title = self.f.sentence()
        param = {'phone': self.f.phone_number(), 'invoiceStatus': 2, 'paymentMethod': 'wechat'}
        kafka_data = {'action': 'UPDATE', "vin": "DEFAULT_VIN", "cpId": cp, "aid": aid, 'param': json.dumps(param),
                      "orderType": "BUSINESS", "title": title, "desc": "zdh测试",
                      "businessState": "SUCCESS_PAY", "price": 6.0,
                      "createdTime": 1600312755440, "timeout": 10, "orderStatus": "WAITING_PAY",
                      "orderSubStatus": "DONE",
                      "delete": False, 'tenantId': 'string', 'epOrderId': ep_order_id, 'payStatus': 'SUCCESS_PAY',
                      "info": business_info, "discountAmount": 0, 'epOrderCode': ep_order_id,
                      "domainId": domain, 'orderCategory': '105'}

        kafka_data = {'key': self.my_json_decoder(kafka_data)}
        msg = {'header': header, 'kafkaData': kafka_data}
        topic = 'order-finished-remind-topic'
        self.send_kafka_msg(topic, msg)

    def sync_invoice_kafka(self, ep_orders:list, invoice, price,aid, domain='GAS', cp='NX_ENGINE'):
        '''
        模拟从kafka发送加油发票信息
        :param ep_orders:EP订单列表
        :param domain: 业务域，默认为GAS
        :param cp: 默认为NX_ENGINE
        :return:
        '''
        header = {'domainId': domain}
        remark = self.f.sentence()
        date = self.time_delta()
        kafka_data = {"action": "INVOICE_UPDATE", "domainId": domain, "epInvoiceId": 10086, "cpId": cp,
                      "serialNo": self.f.md5(), 'tenantId': 'string', "invoiceNo": invoice,
                      "actionId": "action", "aid": aid, "tel": self.f.phone_number(),
                      "phone": "18888888888", "partyType": "COMPANY", "tax": "91310115560364240G", "name": "钛马信息技术有限公司",
                      "addressTel": "02887676543", "bankAccount": "null", "price": price,
                      "remark": remark, "content": "车用汽油/柴油(明细项)", "status": "SUCCESS",
                      "email": self.f.email(), "createTime": date,
                      "transmissionTime": date, "createBy": "system", 'epOrderIds': ep_orders,
                      "createDate": date, "updateBy": "system", "updateDate": date,
                      "remarks": remark, "delFlag": "0"}

        kafka_data = {'key': self.my_json_decoder(kafka_data)}
        msg = {'header': header, 'kafkaData': kafka_data}
        host = '10.20.4.11:9092'
        topic = 'order-finished-remind-topic'
        self.send_kafka_msg(host, topic, msg)

    def invoice_info(self, aid):
        url = self.url + '/sm/order/v1/invoice/header'
        data = {'aid': aid}
        code, body = self.do_get(url, data)
        self.assert_msg(code, body)

    def apply_invoice(self, aid, order_no, duty_no, head, phone):

        url = self.url + '/sm/order/v1/invoice/apply'
        data = {
            'dutyNum': duty_no, 'email': self.f.email(), 'invoiceHead': head, 'phone': phone,
            'invoiceType': '0', 'orderId': order_no, 'remark': self.f.sentence(), 'tel': '02887676543'}
        self.header['aid'] = aid
        code, body = self.do_post(url, data, )
        self.assert_msg(code, body)

    def sync_refund(self, aid, ex_order_no):
        sql_res = self.do_mysql_select('select aid,ex_order_no from `order`', db='fawvw_order')
        sql_res = random.choice(sql_res)
        url = self.url + '/sm/order/v1/order/sync/refund'
        data = {'aid': aid, 'exOrderNo': ex_order_no, 'refundAmount': '1',
                'refundStatus': 'SUCCESS', 'origin': 'EP', 'refundChannel': 'CASH', 'refundType': 'REFUND'}
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)

    def sync_order_pay(self, pay_no, **kwargs):
        '''
        同步支付结果
        '''
        url = self.url + '/sm/order/v1/order/sync/pay'
        data = { 'payOrderNo': pay_no, 'payChannel': 'WE_CHAT', 'payAmount': '1.00',
                'payType': 'APP', 'payTime': self.time_delta(),'payStatus':'SUCCESS',**kwargs}
        code,body = self.do_post(url,data)
        print(body)




if __name__ == '__main__':
    os.environ['ENV'] = 'UAT'
    os.environ['GATE'] = 'false'
    o = Order()
    o.add_order()
    # o.update_order(order_no='20201020101920646233472',aid='1603160360456')
    # o.del_order(order_no='20201020101920646233472',aid='1603160360456')
    # o.sync_order_pay('123',aid='')
    # o.order_detail(aid='9351515',order_no='20201124142350661876544')
    # order_no = o.generate_order_no()['data']
    # o.sync_order(aid='9351524', orderNo=order_no, ex='ex%s'%order_no, origin='SOP1',category='110',
    #              serviceId='MUSIC',spId='CLOUD MUSIC',title='测试支付订单',payAmount=0.01,amount=0.01,
    #              goodsId='123456',brand='VW',businessState='waitingPay',businessStateDesc='be happy')
    # o.sync_refund('111333','202009247772089433')
    # o.apply_invoice(aid='4614907', order_no=['2020092409572288861440'], duty_no='91310115560364240G',
    #                 head='钛马信息技术有限公司', phone='18888888888')
    # ex = ExternalOrder()
    # ex.ex_order_sync()
    # ex_order_no_list = o.do_mysql_select(
    #     'SELECT o.ex_order_no from `order` as o WHERE o.id not IN(SELECT order_id from order_invoice_relation) and o.origin="EP"',
    #     db='fawvw_order')
    # print(ex_order_no_list)
    # orderNo = random.choice(ex_order_no_list)['ex_order_no']
    # serial = random.randint(1000000, 10000000)
    # o.sync_invoice(orderNo, serial)
    # sql = o.do_mysql_select('select * from order_invoice where serial="{}"'.format(serial),'fawvw_order')
    # o.invoice_detail(sql[0]['aid'],sql[0]['invoice_no'])
    # o.teardown_sync(orderNo, serial)
    # res = o.invoice_detail(aid='123',serial_no='qwer1')
    # print(res)
