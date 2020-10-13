import pytest
from box.base import Base

o = Base()

@pytest.fixture()
def del_invoice(request):
    serial,order = None,None
    yield
    print('------开始删除同步的发票-----')
    o.do_mysql_select('delete from order_invoice where serial_no="{}"'.format(serial), 'order')
    o.do_mysql_select(
        'delete from order_invoice_relation where order_id=(select id from `order` where ex_order_no="{}")'.format(
            order), 'order')
    print('------删除发票成功-----')
