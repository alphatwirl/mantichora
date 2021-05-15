# Tai Sakuma <tai.sakuma@gmail.com>
import time

import pytest

from mantichora.hubmp import available_mp_start_methods
from mantichora import mantichora

##__________________________________________________________________||
def task(sleep, ret):
    time.sleep(sleep)
    return ret

##__________________________________________________________________||
params = [
    *[
        pytest.param(
            dict(mode='multiprocessing', mp_start_method=m),
            id=f'multiprocessing-{m}'
        )
        for m in available_mp_start_methods],
    pytest.param(dict(mode='threading'), id='threading')
]

##__________________________________________________________________||
@pytest.mark.parametrize('kwargs', params)
def test_end(kwargs):
    mcore = mantichora(**kwargs)
    mcore.run(task, 0.05, 'result 1')
    mcore.run(task, 0.01, 'result 2')
    mcore.run(task, 0.02, 'result 3')
    returns = mcore.returns()
    assert ['result 1', 'result 2', 'result 3'] == returns
    mcore.end()

##__________________________________________________________________||
@pytest.mark.parametrize('kwargs', params)
def test_with(kwargs):
    with mantichora(**kwargs) as mcore:
        mcore.run(task, 0.05, 'result 1')
        mcore.run(task, 0.01, 'result 2')
        mcore.run(task, 0.02, 'result 3')
        returns = mcore.returns()
        assert ['result 1', 'result 2', 'result 3'] == returns

##__________________________________________________________________||
class MyException(Exception):
    pass

@pytest.mark.parametrize('kwargs', params)
def test_with_raise(kwargs):
    with pytest.raises(MyException):
        with mantichora(**kwargs) as mcore:
            mcore.run(task, 0.05, 'result 1')
            mcore.run(task, 0.01, 'result 2')
            mcore.run(task, 0.02, 'result 3')
            raise MyException

##__________________________________________________________________||
@pytest.mark.parametrize('kwargs', params)
def test_receive_one(kwargs):
    with mantichora(**kwargs) as mcore:
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
@pytest.mark.parametrize('kwargs', params)
def test_receive_finished(kwargs):
    with mantichora(**kwargs) as mcore:
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
