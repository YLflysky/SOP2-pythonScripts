from base.base import Base
import random
import os
import json


class Order(Base):

    def __init__(self):
        super().__init__()
        if self.gate:
            self.url = self.read_conf('sop2_env.conf', self.env, 'host')
        else:
            self.url = self.read_conf('sop2_env.conf', self.env, 'host')

    def update_order_in(self):
        url = self.url + '/order/update'
        num = random.randint(10000000000000000000, 99999999999999999999)
        businessInfo = {'productId': 'code_002', 'price': 111, 'quantity': 1}
        data = {'orderNo': 20200725143430381466944, 'orderCategory': '27262ysyat', 'spId': '080002', 'aid': '9349643',
                'vehModelCode': '040804', 'businessInfo': businessInfo, 'vin': 'LFVSOP2TEST000018', 'serviceId': '08',
                'orderType': 'BUSINESS', 'cpOrderNo': 'MA{}'.format(num), 'title': self.f.sentence(),
                'businessState': 'PROCESSING', 'businessStateDesc': 'SUCCESS', 'amount': 1, 'payAmount': 1,
                'timeout': 30, 'discountAmount': 1}

        code, body = self.do_post(url, data)
        self.assert_msg(code, body)

    def add_order_in(self):
        url = self.url + '/order/create'
        num = random.randint(10000000000000000000, 99999999999999999999)
        businessInfo = {'productId': 'code_002', 'price': 111, 'quantity': 1}
        data = {'orderCategory': '27262ysyat', 'spId': '0082', 'aid': '9349643',
                'vehModelCode': '040804', 'businessInfo': businessInfo, 'vin': 'LFVSOP2TEST000018', 'serviceId': '08',
                'orderType': 'BUSINESS', 'cpOrderNo': 'MA{}'.format(num), 'title': self.f.sentence(),
                'businessState': 'PROCESSING', 'businessStateDesc': 'SUCCESS', 'amount': 1, 'payAmount': 1,
                'timeout': 30, 'discountAmount': 1}
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)
        return body['data']

    def invoice_detail(self, aid, invoice_no):
        '''
        获取发票详情
        :param invoice_no:发票编号，唯一索引
        :param aid:用户id，用于header中

        :return:
        '''

        url = self.url + '/v1/invoice/detail'
        self.header['aid'] = aid
        data = {'invoiceNo': invoice_no}
        code, body = self.do_get(url, data)
        self.assert_msg(code, body)
        return body

    def order_detail(self, aid, order_no):
        url = self.url + '/v1/order/orderNo/{}'.format(order_no)
        code, body = self.do_get(url, params={'aid': aid})
        self.assert_msg(code, body)

    def sync_invoice(self, orderNo, invoiceNo, status, party, ):

        url = self.url + '/v1/invoice/notify/ep/sync'

        data = {'actionId': 'INVOICE_UPDATE', 'aid': '123456', 'domainId': 'COMMON', 'epInvoiceId': '1',
                'epOrderId': orderNo,
                'cpId': 'XIAOMA', 'invoiceNo': invoiceNo, 'partyType': party,
                'bankAccount': self.f.credit_card_number(), 'status': status,
                'remark': self.f.sentence(), 'price': self.f.pyint(), 'createTime': self.time_delta(days=-1),
                'transmissionTime': self.time_delta()}
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)

    def sync_invoice_total(self, data):
        url = self.url + '/v1/invoice/notify/ep/sync'
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)

    def teardown_sync(self, order, invoice):
        print('-----开始teardown------')
        res1 = self.do_mysql_exec('delete from order_invoice where invoice_no={}'.format(invoice), 'order')
        res2 = self.do_mysql_exec(
            'delete from order_invoice_relation where invoice_id=(select id from order_invoice where invoice_no={}'.format(
                invoice),
            'order')
        print('result:{},{}'.format(res1, res2))
        print('同步的发票删除成功')

    def generate_order_no(self):
        url = self.url + '/v1/order/genOrderNo'
        code, body = self.do_get(url, None)
        print(body)
        assert 200 == code
        return body

    def sync_order(self, orderNo, ex_order_no, origin, aid):
        '''
        UAT环境同步订单信息
        :return:
        '''
        url = self.url + '/v1/order/sync'
        data = {'aid': aid, 'detail': {'jojo1': 'code_002', 'jojo2': '111'}, 'timeout': '82726',
                'orderNo': orderNo, 'info': {'productId': 'code_002', 'price': '111', 'quantity': '1'},
                'exOrderNo': ex_order_no, 'delFlag': '2', 'remarks': 'jojo', 'createTime': '159765443334',
                'invoiceStatus': 'FAILED', 'pointsFlag': True, 'pointsNums': '1', 'pointsAmount': '78',
                'couponAmount': '2', 'couponId': '25365', 'vehModelCode': '川A123456', 'vin': 'LJ8E3C1MXGB008988',
                'actualPayAmount': '9', 'discountAmount': '4', 'amount': '5', 'serviceId': '765', 'spId': '987',
                'orderType': 'COMMODITY', 'title': 'BM测试同步订单', 'businessStateDesc': '98', 'businessState': '98',
                'origin': origin, 'orderCategory': '007', 'orderStatus': 'INIT'}

        code, body = self.do_post(url, data)
        self.assert_msg(code, body)

    def sync_order_kafka(self):
        header = {'domainId': 'GAS'}
        aid = self.f.pyint(4, 5)
        ORDER_NO = self.f.ssn()
        kafka_data = {'action': 'ADD', "vin": "DEFAULT_VIN", "cpId": "NX_ENGINE", "aid": aid, "serviceId": "GAS",
                      "orderType": "BUSINESS", "exOrderNo": ORDER_NO, "title": self.f.sentence(),
                      "businessState": "SUCCESS_PAY", "businessStateDesc": "zdh测试", "amount": 6.0, "payAmount": 0,
                      "createdTime": 1600312755440, "timeout": 10, "orderStatus": "FINISH", "orderSubStatus": "DONE",
                      "delete": False, 'tenantId': 'string', 'cpOrderId': ORDER_NO, 'epOrderCode': ORDER_NO,
                      "businessInfo": {"actual": 5.99, "gunNum": "1", "amount": 6, "cpOrderNo": "20200917111619961000",
                                       "cpId": "NX_ENGINE", "discount": 0.01, "createOrderTime": "2020-09-17 11:16:20",
                                       "merchantOrderNo": "36a5ecca-f1ba-4bc2-81af-db231138126f", "couponAmount": 0,
                                       "payType": "WECHAT_PAY", "phone": "18888888888", "oilType": "92",
                                       "payment": "qrcode",
                                       "paymentTime": "2020-09-17 11:18:59", "aid": "4614907", "status": "SUCCESS_PAY",
                                       "stationId": "20b5ed1e47a244a7ac89f4ab42a8f5de"}, "discountAmount": 0,
                      "domainId": "GAS", "origin": "EP", 'orderCategory': '001'}
        kafka_data = {"action": "INVOICE_UPDATE", "domainId": "GAS", "epInvoiceId": 14, "cpId": "NX_ENGINE",
                      "serialNo": "20200922134659640233", "invoiceNo": "38133062",'tenantId':'string',
                      "actionId": "action_20200922134659691000", "aid": "4614907", "tel": "02887676543",
                      "phone": "18888888888", "partyType": "COMPANY", "tax": "91310115560364240G", "name": "钛马信息技术有限公司",
                      "addressTel": "null02887676543", "bankAccount": "nullnull", "price": "5.99",
                      "remark": "虽然两个设计拥有现在比较.", "content": "车用汽油/柴油(明细项)", "status": "SUCCESS",
                      "email": "taocao@yahoo.com", "createTime": "2020-09-22 13:47:00",
                      "transmissionTime": "2020-09-22 13:46:59", "createBy": "system",'epOrderId': '123',
                      "createDate": "2020-09-22 13:47:00", "updateBy": "system", "updateDate": "2020-09-22 14:00:04",
                      "remarks": "虽然两个设计拥有现在比较.", "delFlag": "0"}
        kafka_data = {'key': json.dumps(kafka_data)}
        msg = {'header': header, 'kafkaData': kafka_data}
        host = '10.20.4.11:9092'
        topic = 'order-finished-remind-topic'
        self.send_kafka_msg(host, topic, msg)

    def invoice_info(self, aid):
        url = self.url + '/v1/invoice/header'
        data = {'aid': aid}
        code, body = self.do_get(url, data)
        self.assert_msg(code, body)

    def apply_invoice(self, aid, order_no, duty_no, head):

        url = self.url + '/v1/invoice/apply'
        data = {
            'dutyNum': duty_no, 'email': self.f.email(), 'invoiceHead': head, 'phone': '18888888888',
            'invoiceType': '0', 'orderId': order_no, 'remark': self.f.sentence(), 'tel': '02887676543'}
        self.header['aid'] = aid
        code, body = self.do_post(url, data, )
        self.assert_msg(code, body)

    def sync_refund(self, aid, ex_order_no):
        sql_res = self.do_mysql_select('select aid,ex_order_no from `order`', db='order')
        sql_res = random.choice(sql_res)
        url = self.url + '/v1/order/sync/refund'
        data = {'aid': aid, 'exOrderNo': ex_order_no, 'refundAmount': '1',
                'refundStatus': 'SUCCESS', 'origin': 'EP', 'refundChannel': 'CASH', 'refundType': 'REFUND'}
        code, body = self.do_post(url, data)
        self.assert_msg(code, body)


class ExternalOrder(Base):
    def __init__(self):
        super().__init__()

        if self.gate:
            self.url = self.read_conf('sop2_env.conf', self.env, 'hu_host')
        else:
            self.url = self.read_conf('sop2_env.conf', self.env, 'host_ex')

    def ex_order_sync(self):
        '''
        订单同步外部信息
        :return:
        '''
        url = self.url + '/external/v2/sync/order'
        businessInfo = {}

        abc = {'amount': '100', 'title': '同步订单', 'businessState': 'PROCESSING', 'orderType': 'COMMODITY',
               'vin': '123456',
               'aid': '4613993', 'serviceId': '11', 'spId': '1', 'exOrderNo': '1016192287776772',
               'orderCategory': 'parking', 'businessStateDesc': '不太通aaa', 'payAmount': '1024', 'discountAmount': '100',
               'businessInfo': businessInfo}

        code, body = self.do_post(url, abc)
        self.assert_msg(code, body)

    def get_order_list(self):

        url = self.url + '/test-access/tm/mosc-order-ma/order/api/v2/vins/LFV3A23C1K3161804/orders/list'
        data = {'beginTime': '2020-06-01 14:12:33', 'endTime': '2099-08-11 14:12:33', 'orderCategory': '00',
                'orderStatus': '1000', 'vin': 'LFV3A23C1K3161804', 'pageIndex': '1', 'pageSize': '5'}
        code, body = self.do_get(url, params=data)
        self.assert_msg(code, body)


if __name__ == '__main__':
    os.environ['ENV'] = 'DEV'
    os.environ['GATE'] = 'true'
    o = Order()
    # fakers = o.f
    # for f in fakers:
    #     if 'py' in f:
    #         print(f)
    data = {'actionId': 'UPDATE_INVOICE', 'aid': '123456', 'domainId': 'COMMON', 'epInvoiceId': '1',
            'epOrderId': '20200904132112692745472', 'cpId': 'XIAOMA', 'invoiceNo': 2283680, 'partyType': 'PERSONAL',
            'bankAccount': '377363783294793', 'status': 'SUCCESS', 'price': '10', 'createTime': '2020-09-09 09:12:08',
            'transmissionTime': '2020-09-11 09:12:08'}
    # o.sync_order_kafka()
    # o.order_detail(aid='221',order_no='11953484401634137341')
    # o.sync_order(aid=123, orderNo=1008600, ex_order_no='ex10086', origin='EP')
    # o.sync_refund('221','ex92091521906491713931')
    o.apply_invoice(aid='4614907', order_no=['2020092313422542753248'], duty_no='91310115560364240G',
                    head='钛马信息技术有限公司')
    # ex = ExternalOrder()
    # ex.ex_order_sync()
    # ex_order_no_list = o.do_mysql_select(
    #     'SELECT o.ex_order_no from `order` as o WHERE o.id not IN(SELECT order_id from order_invoice_relation) and o.origin="EP"',
    #     db='order')
    # print(ex_order_no_list)
    # orderNo = random.choice(ex_order_no_list)['ex_order_no']
    # serial = random.randint(1000000, 10000000)
    # o.sync_invoice(orderNo, serial)
    # sql = o.do_mysql_select('select * from order_invoice where serial="{}"'.format(serial),'order')
    # o.invoice_detail(sql[0]['aid'],sql[0]['invoice_no'])
    # o.teardown_sync(orderNo, serial)
    # res = o.invoice_detail(aid='123',serial_no='qwer1')
    # print(res)
