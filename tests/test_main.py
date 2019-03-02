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
## what to test
## - logging
## - receive_one
## - atpbar
## - exception
##__________________________________________________________________||
