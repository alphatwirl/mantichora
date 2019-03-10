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
from mantichora.hub import TaskPackage

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
