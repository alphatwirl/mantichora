# Tai Sakuma <tai.sakuma@gmail.com>
import time

import pytest

from mantichora import mantichora

##__________________________________________________________________||
def task(sleep, ret):
    time.sleep(sleep)
    return ret

##__________________________________________________________________||
def test_end():
    mcore = mantichora()
    mcore.run(task, 0.05, 'result 1')
    mcore.run(task, 0.01, 'result 2')
    mcore.run(task, 0.02, 'result 3')
    returns = mcore.returns()
    assert ['result 1', 'result 2', 'result 3'] == returns
    mcore.end()

##__________________________________________________________________||
def test_with():
    with mantichora() as mcore:
        mcore.run(task, 0.05, 'result 1')
        mcore.run(task, 0.01, 'result 2')
        mcore.run(task, 0.02, 'result 3')
        returns = mcore.returns()
        assert ['result 1', 'result 2', 'result 3'] == returns

##__________________________________________________________________||
class MyException(Exception):
    pass

def test_with_raise():
    with pytest.raises(MyException):
        with mantichora() as mcore:
            mcore.run(task, 0.05, 'result 1')
            mcore.run(task, 0.01, 'result 2')
            mcore.run(task, 0.02, 'result 3')
            raise MyException

##__________________________________________________________________||
def test_receive_one():
    with mantichora() as mcore:
        runids = [
            mcore.run(task, 0.05, 'result 1'),
            mcore.run(task, 0.01, 'result 2'),
            mcore.run(task, 0.02, 'result 3'),
        ]
        pairs = [ ]
        while True:
            p = mcore.receive_one()
            if p is None:
                break
            pairs.append(p)
    expected = [
        (runids[0], 'result 1'),
        (runids[1], 'result 2'),
        (runids[2], 'result 3'),
    ]
    assert sorted(expected) == sorted(pairs)

##__________________________________________________________________||
def test_receive_finished():
    with mantichora() as mcore:
        runids = [
            mcore.run(task, 0.05, 'result 1'),
            mcore.run(task, 0.01, 'result 2'),
            mcore.run(task, 0.02, 'result 3'),
        ]
        pairs = [ ]
        while len(pairs) < 3:
            ps = mcore.receive_finished()
            pairs.extend(ps)
    expected = [
        (runids[0], 'result 1'),
        (runids[1], 'result 2'),
        (runids[2], 'result 3'),
    ]
    assert sorted(expected) == sorted(pairs)

##__________________________________________________________________||
## what to test
## - atpbar

##__________________________________________________________________||
