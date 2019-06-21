# Tai Sakuma <tai.sakuma@gmail.com>
import logging

import pytest

from mantichora.hub import MultiprocessingHub

##__________________________________________________________________||
def task():
    logging.info('doing task')

##__________________________________________________________________||
def test_put(caplog):
    obj = MultiprocessingHub()
    obj.open()
    with caplog.at_level(logging.INFO):
        obj.put(task)
    obj.close()

    assert len(caplog.records) == 1
    assert 'doing task' in caplog.records[0].msg

##__________________________________________________________________||
