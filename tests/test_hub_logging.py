# Tai Sakuma <tai.sakuma@gmail.com>
import logging
import functools

import pytest

from mantichora.hubmp import MultiprocessingHub, available_mp_start_methods
from mantichora.hubthreading import ThreadingHub

##__________________________________________________________________||
Hubs = [
    *[
        pytest.param(
            functools.partial(MultiprocessingHub, mp_start_method=m),
            id=f'mp-{m}'
        )
        for m in available_mp_start_methods],
    pytest.param(ThreadingHub, id='threading')]

##__________________________________________________________________||
def task():
    logging.debug('doing task (debug)')
    logging.info('doing task (info)')
    logging.warning('doing task (warning)')

##__________________________________________________________________||
def test_task(caplog):
    with caplog.at_level(logging.INFO):
        task()

    assert [
        ('root', logging.INFO, 'doing task (info)'),
        ('root', logging.WARNING, 'doing task (warning)')
    ] == caplog.record_tuples

@pytest.mark.parametrize('Hub', Hubs)
def test_put(Hub, caplog):
    obj = Hub()
    obj.open()
    with caplog.at_level(logging.INFO):
        obj.put(task)
        obj.close()

    assert [
        ('root', logging.INFO, 'doing task (info)'),
        ('root', logging.WARNING, 'doing task (warning)')
    ] == caplog.record_tuples

##__________________________________________________________________||
