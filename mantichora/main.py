# Tai Sakuma <tai.sakuma@gmail.com>
from __future__ import print_function

from .hub import MultiprocessingDropbox
from .hub import TaskPackage

##__________________________________________________________________||
class mantichora(object):
    def __init__(self, nworkers=4):
        self.dropbox = MultiprocessingDropbox(nprocesses=nworkers, progressbar=True)
        self.dropbox.open()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type:
            self.terminate()
        self.end()

    def run(self, func, *args, **kwargs):
        return self.dropbox.put(package)

    def returns(self):
        pkgidx_result_pairs = self.receive_all()
        if pkgidx_result_pairs is None:
            return
        results = [r for _, r in pkgidx_result_pairs]
        return results

    def receive_all(self):
        return self.dropbox.receive()

    def terminate(self):
        """terminate

        """
        self.dropbox.terminate()

    def end(self):
        """end

        """
        self.dropbox.close()

##__________________________________________________________________||
