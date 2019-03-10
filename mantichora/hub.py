# Tai Sakuma <tai.sakuma@gmail.com>
from __future__ import print_function
import logging
import multiprocessing
import threading
import collections

from operator import itemgetter

import atpbar

from .worker import Worker

##__________________________________________________________________||
# https://docs.python.org/3/howto/logging-cookbook.html#logging-to-a-single-file-from-multiple-processes
def logger_thread(queue):
    while True:
        record = queue.get()
        if record is None:
            break
        logger = logging.getLogger(record.name)
        logger.handle(record)

##__________________________________________________________________||
TaskPackage = collections.namedtuple('TaskPackage', 'task args kwargs')

##__________________________________________________________________||
class MultiprocessingDropbox(object):
    """A drop box for task packages.

    The tasks will be executed in multiprocessing

    Parameters
    ----------
    nprocesses : int
        The number of processes
    progressbar : bool
        Progress bars from atpbar can be used in spawned processes if
        True.

    """
    def __init__(self, nprocesses=16, progressbar=True):

        if nprocesses <= 0:
            raise ValueError("nprocesses must be at least one: {} is given".format(nprocesses))

        self.progressbar = progressbar

        self.n_max_workers = nprocesses
        self.workers = [ ]
        self.task_queue = multiprocessing.JoinableQueue()
        self.result_queue = multiprocessing.Queue()
        self.logging_queue = multiprocessing.Queue()
        self.lock = multiprocessing.Lock()
        self.n_ongoing_tasks = 0
        self.task_idx = -1 # so it starts from 0

        self._repr_pairs = [
            ('nprocesses', nprocesses),
            ('progressbar', progressbar),
        ]

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(['{}={!r}'.format(n, v) for n, v in self._repr_pairs]),
        )

    def open(self):

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
            worker = Worker(
                task_queue=self.task_queue,
                result_queue=self.result_queue,
                logging_queue=self.logging_queue,
                progressReporter=reporter,
                lock=self.lock
            )
            worker.start()
            self.workers.append(worker)

    def put(self, package):
        self.task_idx += 1
        self.task_queue.put((self.task_idx, package))
        self.n_ongoing_tasks += 1
        return self.task_idx

    def put_multiple(self, packages):
        task_idxs = [ ]
        for package in packages:
            task_idxs.append(self.put(package))
        return task_idxs

    def receive_one(self):
        """return a pair of the package index and result of a task

        This method waits until a task finishes.

        Returns
        -------
        list or None
            a pair of the package index and result of a task.
            `None` if no tasks are outstanding.

        """
        if self.n_ongoing_tasks == 0:
            return None

        self.n_ongoing_tasks -= 1
        return self.result_queue.get() # (task_idx, result)

    def poll(self):
        """Return pairs of task indices and results of finished tasks.
        """

        messages = self._receive_finished()

        # sort in the order of task_idx
        messages = sorted(messages, key=itemgetter(0))

        return messages

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
        for worker in self.workers:
            worker.terminate()

        # wait until all workers are terminated.
        while any([w.is_alive() for w in self.workers]):
            pass

        self.workers = [ ]

    def close(self):

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
