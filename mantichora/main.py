# Tai Sakuma <tai.sakuma@gmail.com>
from __future__ import print_function

from .hub import MultiprocessingDropbox
from .hub import TaskPackage

##__________________________________________________________________||
class mantichora(object):
    """A simple interface to multiprocessing

    https://github.com/alphatwirl/mantichora

    Parameters
    ----------
    nworkers : int, optional
        The number of workers, the default 4.

    """

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
        """run a function in a background process

        Parameters
        ----------
        func : callable
            A function to be run in a background process
        args : list
            Positional parameters to `func`
        kwargs: dict
            Keyword parameters to `func`

        Returns
        -------
        int
            run ID
        """
        package = TaskPackage(task=func, args=args, kwargs=kwargs)
        return self.dropbox.put(package)

    def returns(self):
        """wait until all functions finish running and return a list of return values

        The return values are sorted in the order of the functions which have
        been given to `run()`

        """

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
