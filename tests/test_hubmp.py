# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from mantichora.hubmp import MultiprocessingHub, available_mp_start_methods

##__________________________________________________________________||
def test_at_least_one_method_available():
    assert available_mp_start_methods

##__________________________________________________________________||
@pytest.mark.parametrize('method', available_mp_start_methods)
def test_init_mp_start_method(method):
    hub = MultiprocessingHub(mp_start_method=method)

    assert method == hub.ctx.get_start_method()
    # https://github.com/python/cpython/blob/v3.9.5/Lib/multiprocessing/context.py#L197

    assert method == hub.Worker._start_method
    # https://github.com/python/cpython/blob/v3.9.5/Lib/multiprocessing/context.py#L273

##__________________________________________________________________||
def test_init_raise():
    with pytest.raises(ValueError):
        MultiprocessingHub(mp_start_method='no-such-method')

##__________________________________________________________________||
@pytest.fixture()
def mock_no_available_mp_start_methods(monkeypatch):
    monkeypatch.setattr('mantichora.hubmp.available_mp_start_methods', ())
    yield

def test_no_available_mp_start_methods(mock_no_available_mp_start_methods):
    with pytest.raises(RuntimeError):
        MultiprocessingHub(mp_start_method='spawn')

##__________________________________________________________________||
