# Tai Sakuma <tai.sakuma@gmail.com>
import time
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
    # pytest.param(ThreadingHub, id='threading'),
    ]

# Note: "threading" is commented out because there doesn't seem to be
# a reliable to kill threads in Python

##__________________________________________________________________||
def task_perpetual(ret):
    while True:
        time.sleep(0.001)
    return ret

##__________________________________________________________________||
@pytest.fixture(params=Hubs)
def obj(request):
    ret = request.param()
    ret.open()
    yield ret
    ret.terminate()
    ret.close()

##__________________________________________________________________||
def test_terminate(obj):
    obj.put(functools.partial(task_perpetual, 'result1'))
    obj.put(functools.partial(task_perpetual, 'result2'))
    obj.terminate()

def test_terminate_close(obj):
    obj.put(functools.partial(task_perpetual, 'result1'))
    obj.put(functools.partial(task_perpetual, 'result2'))
    obj.terminate()
    obj.close()

##__________________________________________________________________||
