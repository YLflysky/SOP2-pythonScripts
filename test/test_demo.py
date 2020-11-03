import pytest

@pytest.mark.demo
def test_01():
    assert 1 ==1

@pytest.mark.sergio
def test_02():
    assert 'sergio'

@pytest.mark.lyin
def test_03():
    assert 1 == 2