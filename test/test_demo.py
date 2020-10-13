import pytest
from test import models

def myfunc():
    raise ValueError("Exception 123 raised")


def test_match():
    with pytest.raises(ValueError) as excinfo:
        myfunc()
    assert '123' in str(excinfo.value)


@pytest.fixture(scope='function')
def smtp_connection():
    import smtplib
    return smtplib.SMTP('smtp.163.com',25,timeout=20)

def test_ehlo(smtp_connection):
    res,_ =smtp_connection.ehlo()
    assert res == 250
    print(_)
    assert 0

@pytest.fixture()
def make_customer_record():
    created_records =[]

    def _make_customer_record(name):
        record = models.Customer(name=name,orders=[])
        created_records.append(record)
        return record

    yield _make_customer_record

    #销毁数据
    for record in created_records:
        record.destory()

def test_customer_records(make_customer_record):
    c_1 = make_customer_record('Lisa')
    c_2 = make_customer_record('Mike')
    c_3 = make_customer_record('Meredith')
