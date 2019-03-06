# Tai Sakuma <tai.sakuma@gmail.com>
import logging
import time

import pytest

from mantichora import mantichora

##__________________________________________________________________||
def task(sleep, ret, msg):
    time.sleep(sleep)
    logging.info(msg)
    return ret

##__________________________________________________________________||
def test_logging(caplog):
    with caplog.at_level(logging.INFO):
        with mantichora() as mcore:
            mcore.run(task, 0.05, 'result 1', 'message 1')
            mcore.run(task, 0.01, 'result 2', 'message 2')
            mcore.run(task, 0.02, 'result 3', 'message 3')
            returns = mcore.returns()
            assert ['result 1', 'result 2', 'result 3'] == returns

    assert 3 == len(caplog.records)
    for r in caplog.records:
        assert r.levelname == 'INFO'
    msgs_actual = sorted([r.msg for r in caplog.records])
    msgs_expected = sorted(['message 1', 'message 2', 'message 3'])
    assert msgs_expected == msgs_actual

##__________________________________________________________________||
