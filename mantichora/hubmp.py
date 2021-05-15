# Tai Sakuma <tai.sakuma@gmail.com>
import time
import logging
import multiprocessing
import threading

from operator import itemgetter
from collections import namedtuple

from logging.handlers import QueueHandler

import atpbar

##__________________________________________________________________||
MP_START_METHODS = ('fork', 'spawn', 'forkserver') # in the order of preferences as default

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

def define_worker_class(mp_start_method, ctx):
    """Define a worker class

    e.g.,
    class WorkerFork(WorkerBase, ctx.Process):
        def __init__(self, *args, **kwargs):
            ctx.Process.__init__(self)
            WorkerBase.__init__(self, *args, **kwargs)

    Parameters
    ----------
    mp_start_method : str
        E.g., 'fork', 'spawn','forkserver'
    ctx : object
        A multiprocessing context.

    Returns
    -------
    class

    """

    name = f'Worker{mp_start_method.capitalize()}'
    # e.g., "WorkerFork", "WorkerSpawn", "WorkerForkserver"

    bases = (WorkerBase, ctx.Process)

    def init(self, *args, **kwargs):
        ctx.Process.__init__(self)
        WorkerBase.__init__(self, *args, **kwargs)

    worker_class = type(
        name,
        bases,
        { '__init__': init }
    )
    return worker_class

def is_mp_start_method_available(method):
    try:
        multiprocessing.get_context(method)
    except ValueError:
        return False
    return True

available_mp_start_methods = tuple(m for m in MP_START_METHODS if is_mp_start_method_available(m))
mp_start_method_default = available_mp_start_methods[0] if available_mp_start_methods else None


MpStartMethod = namedtuple('MpStartMethod', ['context', 'Worker'])

mp_start_method_dict = {}
for method in available_mp_start_methods:
    ctx = multiprocessing.get_context(method)
    Worker = define_worker_class(method, ctx)
    mp_start_method_dict[method] = MpStartMethod(context=ctx, Worker=Worker)
    globals()[Worker.__name__] = Worker # for pickle to be able to find the class definition


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
class MultiprocessingHub:
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
    def __init__(self, nworkers=16, progressbar=True, mp_start_method=mp_start_method_default):

        if nworkers <= 0:
            raise ValueError("nworkers must be at least one: {} is given".format(nworkers))

        if not available_mp_start_methods:
            raise RuntimeError("No multiprocessing start methods available!")

        try:
            m = mp_start_method_dict[mp_start_method]
        except KeyError:
            raise ValueError((
                f"Unknown mp_start_method: {mp_start_method!r}. "
                f"Available methods: {available_mp_start_methods!r}. "
            ))

        self.Worker = m.Worker
        self.ctx = m.context

        self.progressbar = progressbar

        self.n_max_workers = nworkers
        self.workers = [ ]
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

        self.task_queue = self.ctx.JoinableQueue()
        self.result_queue = self.ctx.Queue()
        self.logging_queue = self.ctx.Queue()

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
            time.sleep(0.0001)

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
            time.sleep(0.0001)

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
        try:
            self.logging_queue.put(None)
        except (AssertionError, ValueError):
            # the queue is already closed
            # AssertionError: Python 3.7
            # ValueError: Python 3.8+
            pass
        self.loggingListener.join()

        self.task_queue.close()
        self.result_queue.close()
        self.logging_queue.close()

        if self.progressbar:
            atpbar.flush()

##__________________________________________________________________||
