import pytest


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