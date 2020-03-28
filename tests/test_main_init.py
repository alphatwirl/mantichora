# Tai Sakuma <tai.sakuma@gmail.com>
import pytest

from mantichora import mantichora

##__________________________________________________________________||
def test_init_raise():
    with pytest.raises(ValueError):
        mantichora(mp_start_method='no-such-method')

##__________________________________________________________________||
@pytest.mark.parametrize('mp_start_method', ['fork', 'spawn', 'forkserver'])
def test_init_mp_start_method(mp_start_method):
    with mantichora(mp_start_method=mp_start_method):
        pass

##__________________________________________________________________||
