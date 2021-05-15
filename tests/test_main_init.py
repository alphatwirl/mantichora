# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from mantichora.hubmp import available_mp_start_methods
from mantichora import mantichora

##__________________________________________________________________||
@pytest.mark.parametrize('mp_start_method', available_mp_start_methods)
def test_init_mp_start_method(mp_start_method):
    with mantichora(mp_start_method=mp_start_method):
        pass

def test_init_mp_start_method_raise():
    with pytest.raises(ValueError):
        mantichora(mp_start_method='no-such-method')

##__________________________________________________________________||
@pytest.mark.parametrize('mode', ['multiprocessing', 'threading'])
def test_init_mode(mode):
    with mantichora(mode=mode):
        pass

def test_init_mode_raise():
    with pytest.raises(ValueError):
        mantichora(mode='no-such-mode')

##__________________________________________________________________||
