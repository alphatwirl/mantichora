# Tai Sakuma <tai.sakuma@gmail.com>
import threading

try:
    import queue
except ImportError:
    # Python 2.7
    import Queue as queue

from operator import itemgetter

import atpbar

##__________________________________________________________________||
class ThreadingHub(object):
    """A hub for Threading

    Parameters
    ----------
    nworkers : int
        The number of threads

    """
    def __init__(self, nworkers=16):

        if nworkers <= 0:
            raise ValueError("nworkers must be at least one: {} is given".format(nworkers))

        self.n_max_workers = nworkers
        self.workers = [ ]
        self.task_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.n_ongoing_tasks = 0
        self.task_idx = -1 # so it starts from 0

        self._repr_pairs = [
            ('nworkers', nworkers),
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

        # start workers
        for i in range(self.n_max_workers):
            worker = Worker(
                task_queue=self.task_queue,
                result_queue=self.result_queue
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
        """terminate running tasks (not implemented)

        Returns
        -------
        None
        """
        pass

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

        atpbar.flush()

##__________________________________________________________________||
class Worker(threading.Thread):
    def __init__(self, task_queue, result_queue):
        threading.Thread.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        try:
            self._run_tasks()
        except KeyboardInterrupt:
            pass

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

##__________________________________________________________________||
