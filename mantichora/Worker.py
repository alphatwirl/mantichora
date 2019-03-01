# Tai Sakuma <tai.sakuma@gmail.com>
import multiprocessing
import logging
# import logging.handlers

try:
    from logging.handlers import QueueHandler
except ImportError:
    from .queuehandler import QueueHandler

from atpbar import register_reporter

##__________________________________________________________________||
class Worker(multiprocessing.Process):
    def __init__(self, task_queue, result_queue, logging_queue,
                 lock, progressReporter):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.logging_queue = logging_queue
        self.lock = lock
        self.progressReporter = progressReporter

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
        register_reporter(self.progressReporter)

    def _run_tasks(self):
        while True:
            message = self.task_queue.get()
            if message is None:
                self.task_queue.task_done()
                break
            task_idx, package = message
            result = package.task(*package.args, **package.kwargs)
            self.task_queue.task_done()
            self.result_queue.put((task_idx, result))


##__________________________________________________________________||
