from time import sleep

from core.base import CheckFunctionsCollectionMixin


class SimpleChecker(CheckFunctionsCollectionMixin):
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
