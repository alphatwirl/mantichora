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
        self.terminate()
        self.end()

    def run(self, func, *args, **kwargs):
        """run a task function in a background process

        Parameters
        ----------
        func : callable
            A task function to be run in a background process
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
        """return a list of return values of the task functions

        The return values are sorted in the order of the task
        functions which have been given to `run()`

        This method waits until all task functions finish.

        Returns
        -------
        list
            return values of the task functions

        """
        pairs = self.receive_all() # list of pairs (runid, result)
        return [p[1] for p in pairs]

    def receive_one(self):
        """return a pair of the run ID and return value of a task function

        This method waits until one task function finishes.

        Returns
        -------
        list or None
            a pair of the run ID and return value of a task function.
            `None` if no task functions are outstanding.

        """
        return self.dropbox.receive_one()

    def receive_finished(self):
        """return pairs of the run IDs and return values of finished task function

        This method doesn't wait.

        Returns
        -------
        list or None
            pairs of the run IDs and return values of task functions.
            `None` if no task functions are outstanding.

        """
        return self.dropbox.poll()

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
