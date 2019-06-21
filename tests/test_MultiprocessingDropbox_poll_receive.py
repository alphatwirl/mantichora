# Tai Sakuma <tai.sakuma@gmail.com>
import time
import functools

import pytest

from mantichora.hubmp import MultiprocessingHub

##__________________________________________________________________||
@pytest.fixture()
def obj():
    ret = MultiprocessingHub()
    ret.open()
    yield ret
    ret.terminate()
    ret.close()

def task(sleep, ret):
    time.sleep(sleep)
    return ret

@pytest.fixture()
def expected(obj):
    idx1 = obj.put(functools.partial(task, 0.010, 'result1'))
    idx2 = obj.put(functools.partial(task, 0.001, 'result2'))
    idx3 = obj.put(functools.partial(task, 0.005, 'result3'))
    idx4 = obj.put(functools.partial(task, 0.002, 'result4'))
    ret = [
        (idx1, 'result1'),
        (idx2, 'result2'),
        (idx3, 'result3'),
        (idx4, 'result4'),
    ]
    ret = sorted(ret)
    return ret

##__________________________________________________________________||
def test_poll(obj, expected):
    actual = [ ]
    while len(actual) < len(expected):
        actual.extend(obj.poll())
    assert expected == sorted(actual)

def test_poll_then_receive(obj, expected):
    actual = [ ]
    while not actual:
        actual.extend(obj.poll())
    actual.extend(obj.receive())
    assert expected == sorted(actual)

##__________________________________________________________________||
def test_receive_one(obj, expected):
    time.sleep(0.005) # so multiple jobs finish
    actual = [ ]
    for i in range(len(expected)):
        actual.append(obj.receive_one())
    assert obj.receive_one() is None
    assert expected == sorted(actual)

def test_receive_one_then_receive(obj, expected):
    time.sleep(0.005) # so multiple jobs finish
    actual = [ ]
    actual.append(obj.receive_one())
    actual.extend(obj.receive())
    assert expected == sorted(actual)

def test_receive_one_then_poll(obj, expected):
    time.sleep(0.005) # so multiple jobs finish
    actual = [ ]
    actual.append(obj.receive_one())
    while len(actual) < len(expected):
        actual.extend(obj.poll())
    assert expected == sorted(actual)

def test_poll_then_receive_one(obj, expected):
    actual = [ ]
    while not actual:
        actual.extend(obj.poll())
    while len(actual) < len(expected):
        actual.append(obj.receive_one())
    assert obj.receive_one() is None
    assert expected == sorted(actual)

##__________________________________________________________________||
