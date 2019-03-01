# Tai Sakuma <tai.sakuma@gmail.com>
from .hub import MultiprocessingDropbox
from .TaskPackage import TaskPackage

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
