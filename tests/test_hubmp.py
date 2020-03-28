# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from mantichora.hubmp import MultiprocessingHub
from mantichora.hubmp import ctx_fork, WorkerFork
from mantichora.hubmp import ctx_spawn, WorkerSpawn
from mantichora.hubmp import ctx_forkserver, WorkerForkserver

##__________________________________________________________________||
def test_init_raise():
    with pytest.raises(ValueError):
        MultiprocessingHub(mp_start_method='no-such-method')

##__________________________________________________________________||
params = [
    pytest.param('fork', ctx_fork, WorkerFork, id='fork'),
    pytest.param('spawn', ctx_spawn, WorkerSpawn, id='spawn'),
    pytest.param('forkserver', ctx_forkserver, WorkerForkserver, id='forkserver')
]
@pytest.mark.parametrize('mode, ctx, Worker', params)
def test_init_mp_start_method(mode, ctx, Worker):
    hub = MultiprocessingHub(mp_start_method=mode)
    assert ctx is hub.ctx
    assert Worker is hub.Worker

##__________________________________________________________________||
