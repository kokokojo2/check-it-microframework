import asyncio
import threading
from time import sleep
from functools import wraps
from itertools import repeat
from concurrent import futures

from core.base import CheckFunctionsCollectionMixin, LoggingMixin


class SimpleChecker(CheckFunctionsCollectionMixin, LoggingMixin):
    """
    Runs the user-defined set of jobs (that consist of a checking function, callback and time to sleep) in a sequential
    single-threaded manner. Please note that if sleep time for a job is specified, the execution of the loop will be
    paused completely (that is block all other checks that are being run by this checker).
    """

    def __init__(self, enable_logging=False, custom_logger=None):
        CheckFunctionsCollectionMixin.__init__(self)
        LoggingMixin.__init__(self, enable_logging, custom_logger)

    def run(self, loop=True):
        self.logger.info(f'The checker is starting to run the jobs.')
        while loop:
            for name, job in self.job_storage.items():
                self.logger.info(f'Job "{name}" is running...')
                self.run_job(job)

    def run_job(self, job):
        func, callback, sleep_time = self.unpack_job(job)
        self.logger.info(f'Running the function "{func.__name__}".')
        result = func()

        if callback:
            self.logger.info(f'Running the callback "{callback.__name__}".')
            callback(result)

        if sleep_time:
            self.logger.info(f'Sleeping for {sleep_time} seconds.')
            sleep(sleep_time)


class AsyncChecker(CheckFunctionsCollectionMixin, LoggingMixin):
    """
    Runs the user-defined set of jobs (that consist of a checking function, callback and time to sleep) in an async
    manner. Each checking function or a callback has to be async. The sleep is not blocking,
    thus the checker will switch to another job during a sleep call.
    """

    def __init__(self, enable_logging=False, custom_logger=None):
        CheckFunctionsCollectionMixin.__init__(self)
        LoggingMixin.__init__(self, enable_logging, custom_logger)

    def run(self, loop=True):
        # the loop argument is never used and is added to persist the same function signature among different checkers
        self.logger.info(f'The checker is starting to run the jobs.')
        asyncio.run(self._run())

    async def _run(self):
        tasks = [asyncio.create_task(self.run_job(job)) for name, job in self.job_storage.items()]
        await asyncio.gather(*tasks)

    async def run_job(self, job):
        func, callback, sleep_time = self.unpack_job(job)

        while True:
            self.logger.info(f'Running the function "{func.__name__}".')
            result = await func()

            if callback:
                self.logger.info(f'Running the callback "{callback.__name__}".')
                await callback(result)

            if sleep_time:
                self.logger.info(f'Sleeping for {sleep_time} seconds.')
                await asyncio.sleep(sleep_time)


class MultiThreadedChecker(SimpleChecker):

    @staticmethod
    def make_event_based_runner(func):
        @wraps(func)
        def runner(*args, **kwargs):
            run_event = kwargs.pop('run_event')
            while run_event.is_set():
                func(*args, **kwargs)

        return runner

    run_job = make_event_based_runner(SimpleChecker.run_job)

    def run(self, loop=True):
        # the loop argument is never used and is added to persist the same function signature among different checkers
        run_event = threading.Event()
        run_event.set()

        self.logger.info(f'The checker is starting to run the jobs.')

        try:
            with futures.ThreadPoolExecutor(max_workers=len(self.job_storage)) as executor:
                executor.map(
                    lambda job, event: self.run_job(job, run_event=event),
                    self.job_storage.values(),
                    repeat(run_event)
                )
        except KeyboardInterrupt:
            run_event.clear()
