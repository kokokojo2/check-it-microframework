import asyncio
from time import sleep

from core.base import CheckFunctionsCollectionMixin


class SimpleChecker(CheckFunctionsCollectionMixin):
    """
    Runs the user-defined set of jobs (that consist of a checking function, callback and time to sleep) in a sequential
    single-threaded manner. Please note that if sleep time for a job is specified, the execution of the loop will be
    paused completely (that is block all other checks that are being run by this checker).
    """

    def run(self, loop=True):
        while loop:
            for name, job in self.job_storage.items():
                self.run_job(job)

    def run_job(self, job):
        func = job['checker']
        callback = job.get('callback', None)
        sleep_time = job.get('sleep_time', None)

        result = func()

        if callback:
            callback(result)

        if sleep_time:
            sleep(sleep_time)
