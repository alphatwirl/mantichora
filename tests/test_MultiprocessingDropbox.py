# Tai Sakuma <tai.sakuma@gmail.com>
import os
import time
import collections

import pytest

try:
    import unittest.mock as mock
except ImportError:
    import mock

from alphatwirl.concurrently import MultiprocessingDropbox
from alphatwirl.concurrently import TaskPackage

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
class MockProgressReporter(object):
    pass

@pytest.fixture()
def mock_progressmonitor():
    ret = mock.MagicMock()
    ret.create_reporter.return_value = MockProgressReporter()
    return ret

@pytest.fixture()
def obj(mock_progressmonitor):
    ret = MultiprocessingDropbox(progressMonitor=mock_progressmonitor)
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
def test_poll(obj, package1, package2, package3, package4):
    packages = [package1, package2, package3, package4]
    pkgidxs = obj.put_multiple(packages)

    expected = [
        (i, MockResult(name=p.task.name, args=p.args, kwargs=p.kwargs))
        for i, p in zip(pkgidxs, packages)]

    actual = [ ]
    while len(actual) < len(expected):
        actual.extend(obj.poll())
    assert sorted(expected) == sorted(actual)

def test_poll_then_receive(obj, package1, package2, package3, package4):
    packages = [package1, package2, package3, package4]
    pkgidxs = obj.put_multiple(packages)

    expected = [
        (i, MockResult(name=p.task.name, args=p.args, kwargs=p.kwargs))
        for i, p in zip(pkgidxs, packages)]

    actual = [ ]
    while not actual:
        actual.extend(obj.poll())

    actual.extend(obj.receive())

    assert sorted(expected) == sorted(actual)

##__________________________________________________________________||
def test_receive_one(obj, package1, package2, package3, package4):
    packages = [package1, package2, package3, package4]
    pkgidxs = obj.put_multiple(packages)

    expected = [
        (i, MockResult(name=p.task.name, args=p.args, kwargs=p.kwargs))
        for i, p in zip(pkgidxs, packages)]

    actual = [ ]
    actual.append(obj.receive_one())
    actual.append(obj.receive_one())
    actual.append(obj.receive_one())
    actual.append(obj.receive_one())
    assert obj.receive_one() is None
    assert sorted(expected) == sorted(actual)

def test_receive_one_then_receive(obj, package1, package2, package3, package4):
    packages = [package1, package2, package3, package4]
    pkgidxs = obj.put_multiple(packages)

    expected = [
        (i, MockResult(name=p.task.name, args=p.args, kwargs=p.kwargs))
        for i, p in zip(pkgidxs, packages)]

    time.sleep(0.005) # so multiple jobs finish

    actual = [ ]
    actual.append(obj.receive_one())

    actual.extend(obj.receive())

    assert sorted(expected) == sorted(actual)

def test_receive_one_then_poll(obj, package1, package2, package3, package4):
    packages = [package1, package2, package3, package4]
    pkgidxs = obj.put_multiple(packages)

    expected = [
        (i, MockResult(name=p.task.name, args=p.args, kwargs=p.kwargs))
        for i, p in zip(pkgidxs, packages)]

    time.sleep(0.005) # so multiple jobs finish

    actual = [ ]
    actual.append(obj.receive_one())

    while len(actual) < len(expected):
        actual.extend(obj.poll())

    assert sorted(expected) == sorted(actual)

##__________________________________________________________________||
