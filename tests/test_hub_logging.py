# Tai Sakuma <tai.sakuma@gmail.com>
import logging

import pytest

from mantichora.hubmp import MultiprocessingHub

##__________________________________________________________________||
Hubs = [MultiprocessingHub]

##__________________________________________________________________||
def task():
    logging.info('doing task')

##__________________________________________________________________||
@pytest.mark.parametrize('Hub', Hubs)
def test_put(Hub, caplog):
    obj = Hub()
    obj.open()
    with caplog.at_level(logging.INFO):
        obj.put(task)
    obj.close()

    assert len(caplog.records) == 1
    assert 'doing task' in caplog.records[0].msg

##__________________________________________________________________||
