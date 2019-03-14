# Tai Sakuma <tai.sakuma@gmail.com>
import os
import time
import collections

import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from mantichora.hub import MultiprocessingDropbox
from mantichora.main import TaskPackage

##__________________________________________________________________||
def test_init_raise():
    with pytest.raises(ValueError):
        MultiprocessingDropbox(nprocesses=0)

def test_open_close():
    obj = MultiprocessingDropbox()
    obj.open()
    obj.close()

def test_open_open_close():
    obj = MultiprocessingDropbox()
    obj.open()
    obj.open() # don't create workers again
    obj.close()

def test_repr():
    obj = MultiprocessingDropbox()
    repr(obj)

##__________________________________________________________________||
MockResult = collections.namedtuple('MockResult', 'name args kwargs')

class MockTask(object):
    def __init__(self, name, time):
        self.name = name
        self.time = time

    def __call__(self, *args, **kwargs):
        time.sleep(self.time)
        return MockResult(name=self.name, args=args, kwargs=kwargs)

##__________________________________________________________________||
@pytest.fixture()
def package1():
    task = MockTask(name='task1', time=0.010)
    args = (111, 222)
    kwargs = dict(A='abc', B='def')
    return TaskPackage(task=task, args=args, kwargs=kwargs)

@pytest.fixture()
def package2():
    task = MockTask(name='task2', time=0.001)
    args = ( )
    kwargs = { }
    return TaskPackage(task=task, args=args, kwargs=kwargs)

@pytest.fixture()
def package3():
    task = MockTask(name='task3', time=0.005)
    args = (33, 44)
    kwargs = { }
    return TaskPackage(task=task, args=args, kwargs=kwargs)

@pytest.fixture()
def package4():
    task = MockTask(name='task4', time=0.002)
    args = ( )
    kwargs = dict(ABC='abc', DEF='def')
    return TaskPackage(task=task, args=args, kwargs=kwargs)

##__________________________________________________________________||
@pytest.fixture()
def obj():
    ret = MultiprocessingDropbox()
    ret.open()
    yield ret
    ret.terminate()
    ret.close()

##__________________________________________________________________||
def test_put(obj, package1, package2):
    assert 0 == obj.put(package1)
    assert 1 == obj.put(package2)

def test_put_multiple(obj, package1, package2):
    assert [0, 1] == obj.put_multiple([package1, package2])

def test_put_receive(obj, package1, package2):
    packages = [package1, package2]
    pkgidxs = [ ]
    for p in packages:
        pkgidxs.append(obj.put(p))

    expected = [
        (i, MockResult(name=p.task.name, args=p.args, kwargs=p.kwargs))
        for i, p in zip(pkgidxs, packages)]
    actual = obj.receive()
    assert expected == actual

def test_receive_order(obj, package1, package2, package3):
    # results of tasks are sorted in the order in which the tasks are put.

    packages = [package1, package2, package3]
    pkgidxs = [ ]
    for p in packages:
        pkgidxs.append(obj.put(p))

    expected = [
        (i, MockResult(name=p.task.name, args=p.args, kwargs=p.kwargs))
        for i, p in zip(pkgidxs, packages)]
    actual = obj.receive()
    assert expected == actual

def test_put_receive_repeat(obj, package1, package2, package3, package4):

    packages = [package1, package2]
    pkgidxs = [ ]
    for p in packages:
        pkgidxs.append(obj.put(p))

    expected = [
        (i, MockResult(name=p.task.name, args=p.args, kwargs=p.kwargs))
        for i, p in zip(pkgidxs, packages)]
    actual = obj.receive()
    assert expected == actual

    packages = [package3, package4]
    pkgidxs = [ ]
    for p in packages:
        pkgidxs.append(obj.put(p))

    expected = [
        (i, MockResult(name=p.task.name, args=p.args, kwargs=p.kwargs))
        for i, p in zip(pkgidxs, packages)]
    actual = obj.receive()
    assert expected == actual

def test_begin_put_recive_end_repeat(obj, package1, package2):
    obj.put(package1)
    obj.receive()
    obj.close()
    obj.open()
    obj.put(package2)
    obj.receive()

def test_terminate(obj, package1, package2):
    obj.put(package1)
    obj.put(package2)
    obj.terminate()

def test_terminate_close(obj, package1, package2):
    obj.put(package1)
    obj.put(package2)
    obj.terminate()
    obj.close()

def test_receive_without_put(obj):
    assert [ ] == obj.receive()

##__________________________________________________________________||
