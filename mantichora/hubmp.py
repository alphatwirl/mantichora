# Tai Sakuma <tai.sakuma@gmail.com>
import logging
import multiprocessing
import threading

from operator import itemgetter

try:
    from logging.handlers import QueueHandler
except ImportError:
    from .queuehandler import QueueHandler

import atpbar

##__________________________________________________________________||
class MultiprocessingHub(object):
    """A hub for multiprocessing.

    Parameters
    ----------
    nworkers : int
        The number of processes
    progressbar : bool
        Progress bars from atpbar can be used in spawned processes if
        True.
    mp_start_method : str, 'fork', 'spawn','forkserver'

    """
    def __init__(self, nworkers=16, progressbar=True, mp_start_method='fork'):

        if nworkers <= 0:
            raise ValueError("nworkers must be at least one: {} is given".format(nworkers))

        if mp_start_method == 'fork':
            self.Worker = WorkerFork
            self.ctx = ctx_fork
        elif mp_start_method == 'spawn':
            self.Worker = WorkerSpawn
            self.ctx = ctx_spawn
        elif mp_start_method == 'forkserver':
            self.Worker = WorkerForkserver
            self.ctx = ctx_forkserver
        else:
            raise ValueError(("'mp_start_method' must be one of "
                              "'fork', 'spawn', 'forkserver': "
                              "'{}' is given").format(mp_start_method))

        self.progressbar = progressbar

        self.n_max_workers = nworkers
        self.workers = [ ]
        self.task_queue = self.ctx.JoinableQueue()
        self.result_queue = self.ctx.Queue()
        self.logging_queue = self.ctx.Queue()
        self.n_ongoing_tasks = 0
        self.task_idx = -1 # so it starts from 0

        self._repr_pairs = [
            ('nworkers', nworkers),
            ('progressbar', progressbar),
        ]

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{}={!r}'.format(n, v) for n, v in self._repr_pairs]),
        )

    def open(self):
        """open the drop box

        This method needs to be called before a task is put.

        Returns
        -------
        None
        """

        if len(self.workers) >= self.n_max_workers:
            # workers already created
            return

        # start logging listener
        self.loggingListener = threading.Thread(
            target=logger_thread, args=(self.logging_queue,)
        )
        self.loggingListener.start()

        # start progress monitor
        if self.progressbar:
            reporter = atpbar.find_reporter()
        else:
            reporter = None

        # start workers
        for i in range(self.n_max_workers):
            worker = self.Worker(
                task_queue=self.task_queue,
                result_queue=self.result_queue,
                logging_queue=self.logging_queue,
                progress_reporter=reporter
            )
            worker.start()
            self.workers.append(worker)

    def put(self, task_func):
        """put a task

        The task will be executed in a background process

        Parameters
        ----------
        task_func : callable
            a task function

        Returns
        -------
        int
            The task index

        """
        self.task_idx += 1
        self.task_queue.put((self.task_idx, task_func))
        self.n_ongoing_tasks += 1
        return self.task_idx

    def put_multiple(self, task_funcs):
        """put a list of tasks

        The tasks will be executed in background processes

        Parameters
        ----------
        task_funcs : list
            a list of task functions

        Returns
        -------
        list
            The list of the task indices

        """
        task_idxs = [ ]
        for t in task_funcs:
            task_idxs.append(self.put(t))
        return task_idxs

    def receive_one(self):
        """return a pair of the task index and result of a task

        This method waits until a task finishes.

        Returns
        -------
        list or None
            a pair of the task index and result of a task.
            `None` if no tasks are outstanding.

        """
        if self.n_ongoing_tasks == 0:
            return None

        self.n_ongoing_tasks -= 1
        return self.result_queue.get() # (task_idx, result)

    def poll(self):
        """Return pairs of task indices and results of finished tasks.
        """
        return self._receive_finished()

    def receive(self):
        """Return pairs of task indices and results.

        This method waits until all tasks finish.
        """

        messages = [ ] # a list of (task_idx, result)
        while self.n_ongoing_tasks >= 1:
            messages.extend(self._receive_finished())

        # sort in the order of task_idx
        messages = sorted(messages, key=itemgetter(0))

        if self.progressbar:
            atpbar.flush()

        return messages

    def _receive_finished(self):
        messages = [ ] # a list of (task_idx, result)
        while not self.result_queue.empty():
            message = self.result_queue.get()
            messages.append(message)
            self.n_ongoing_tasks -= 1
        return messages

    def terminate(self):
        """terminate running tasks

        Returns
        -------
        None
        """

        for worker in self.workers:
            worker.terminate()

        # wait until all workers are terminated.
        while any([w.is_alive() for w in self.workers]):
            pass

        self.workers = [ ]

    def close(self):
        """close the drop box

        Returns
        -------
        None
        """

        # end workers
        if self.workers:
            for i in range(len(self.workers)):
                self.task_queue.put(None)
            self.task_queue.join()
            self.workers = [ ]

        # end logging listener
        self.logging_queue.put(None)
        self.loggingListener.join()

        if self.progressbar:
            atpbar.flush()

##__________________________________________________________________||
class WorkerBase:
    def __init__(self, task_queue, result_queue, logging_queue,
                 progress_reporter):
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.logging_queue = logging_queue
        self.progress_reporter = progress_reporter

    def run(self):
        self._configure_logger()
        self._configure_progressbar()
        try:
            self._run_tasks()
        except KeyboardInterrupt:
            pass

    def _configure_logger(self):
        handler = QueueHandler(self.logging_queue)
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)

    def _configure_progressbar(self):
        atpbar.register_reporter(self.progress_reporter)

    def _run_tasks(self):
        while True:
            message = self.task_queue.get()
            if message is None:
                self.task_queue.task_done()
                break
            task_idx, task_func = message
            result = task_func()
            self.task_queue.task_done()
            self.result_queue.put((task_idx, result))

ctx_fork = multiprocessing.get_context('fork')
ctx_spawn = multiprocessing.get_context('spawn')
ctx_forkserver = multiprocessing.get_context('forkserver')

class WorkerFork(WorkerBase, ctx_fork.Process):
    def __init__(self, *args, **kwargs):
        ctx_fork.Process.__init__(self)
        WorkerBase.__init__(self, *args, **kwargs)

class WorkerSpawn(WorkerBase, ctx_spawn.Process):
    def __init__(self, *args, **kwargs):
        ctx_spawn.Process.__init__(self)
        WorkerBase.__init__(self, *args, **kwargs)

class WorkerForkserver(WorkerBase, ctx_forkserver.Process):
    def __init__(self, *args, **kwargs):
        ctx_forkserver.Process.__init__(self)
        WorkerBase.__init__(self, *args, **kwargs)

##__________________________________________________________________||
# https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
def logger_thread(queue):
    while True:
        record = queue.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        if logger.getEffectiveLevel() <= record.levelno:
            logger.handle(record)

##__________________________________________________________________||
