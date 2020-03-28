# Tai Sakuma <tai.sakuma@gmail.com>
from __future__ import print_function

from .hubmp import MultiprocessingHub

##__________________________________________________________________||
class TaskPackage(object):
    """A task package

    Note: This class will be replaced with `functools.partial`

    """
    def __init__(self, task, args, kwargs):
        self.task = task
        self.args = args
        self.kwargs = kwargs
    def __call__(self):
        return self.task(*self.args, **self.kwargs)

##__________________________________________________________________||
class mantichora(object):
    """A simple interface to multiprocessing

    https://github.com/alphatwirl/mantichora

    Parameters
    ----------
    nworkers : int, optional
        The number of workers, the default 4.
    mp_start_method : str, 'fork', 'spawn','forkserver'
        The start method of multiprocessing. The default `fork`.
        Each method is described in
        https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
        On Jupyter Notebook, the 'fork' method is typically the best
        choice.
        The 'spawn' and "forkserver" have extra restrictions, for
        example, on how the main module is written. The restrictions
        are described at
        https://docs.python.org/3/library/multiprocessing.html#the-spawn-and-forkserver-start-methods
        On MacOS, in the 'fork' method, errors with the message "may
        have been in progress in another thread when fork() was
        called" might occur. This error might be resolved if the
        environment variable 'OBJC_DISABLE_INITIALIZE_FORK_SAFETY' is
        set 'YES' as suggested in
        https://stackoverflow.com/questions/50168647/multiprocessing-causes-python-to-crash-and-gives-an-error-may-have-been-in-progr

    """

    def __init__(self, nworkers=4, mp_start_method='fork'):
        self.hub = MultiprocessingHub(
            nworkers=nworkers, progressbar=True,
            mp_start_method=mp_start_method)
        self.hub.open()

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
        task_func = TaskPackage(task=func, args=args, kwargs=kwargs)
        return self.hub.put(task_func)

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
        return self.hub.receive_one()

    def receive_finished(self):
        """return pairs of the run IDs and return values of finished task function

        This method doesn't wait.

        Returns
        -------
        list or None
            pairs of the run IDs and return values of task functions.
            `None` if no task functions are outstanding.

        """
        return self.hub.poll()

    def receive_all(self):
        return self.hub.receive()

    def terminate(self):
        """terminate

        """
        self.hub.terminate()

    def end(self):
        """end

        """
        self.hub.close()

##__________________________________________________________________||
