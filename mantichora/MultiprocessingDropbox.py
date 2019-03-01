# Tai Sakuma <tai.sakuma@gmail.com>
from __future__ import print_function
import logging
import multiprocessing
import threading

from operator import itemgetter
from collections import deque

import atpbar

from .TaskPackage import TaskPackage

from .Worker import Worker

from alphatwirl.misc.deprecation import _deprecated_class_method_option
import alphatwirl

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
    @_deprecated_class_method_option('progressMonitor')
    def __init__(self, nprocesses=16, progressMonitor=None, progressbar=True):

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

        self.to_return = deque()

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

    def poll(self):
        """Return pairs of task indices and results of finished tasks.
        """

        messages = list(self.to_return) # a list of (task_idx, result)
        self.to_return.clear()

        messages.extend(self._receive_finished())

        # sort in the order of task_idx
        messages = sorted(messages, key=itemgetter(0))

        return messages

    def receive_one(self):
        """Return a pair of a package index and a result.

        This method waits until a task finishes.
        This method returns None if no task is running.
        """

        if self.to_return:
            return self.to_return.popleft()

        if self.n_ongoing_tasks == 0:
            return None

        while not self.to_return:
            self.to_return.extend(self._receive_finished())

        return self.to_return.popleft()


    def receive(self):
        """Return pairs of task indices and results.

        This method waits until all tasks finish.
        """

        messages = list(self.to_return) # a list of (task_idx, result)
        self.to_return.clear()

        while self.n_ongoing_tasks >= 1:
            messages.extend(self._receive_finished())

        # sort in the order of task_idx
        messages = sorted(messages, key=itemgetter(0))

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
