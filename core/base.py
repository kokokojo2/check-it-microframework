from functools import update_wrapper


class CallbackWrapper:
    """The wrapper that is returned by the CheckFunctionsCollectionMixin.check and automatically updates the job with
     the callback function that is decorated with the callback method."""
    def __init__(self, func, checker):
        self.func = func
        self.checker = checker
        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    # should be used as a decorator
    def callback(self, callback_func):
        self.checker.add_job(self.func, callback_func)
        return callback_func


class CheckFunctionsCollectionMixin:
    """
    This mixin provides a piece of functionality that collects the user-defined checker functions.To inform the app that
    a function should be run as a part of the checker`s routine just decorate it with check method.
    """

    def __init__(self):
        self.job_storage = {}
        self.wrapper = CallbackWrapper

    # should be used as a decorator
    def check(self, sleep_time=None):
        """
        This is a decorator method that adds the target function to the checker`s loop.
        :param sleep_time: an optional amount of time in seconds to sleep after the end of a job.
        """
        def check(func):
            self.add_job(func, sleep_time=sleep_time)
            wrapper = self.wrapper(func, self)
            return wrapper
        return check

    def add_job(self, func, callback=None, sleep_time=None, job_name=None):
        """
        Adds a job (that consists of the objects listed below) to the storage in order to run it when the checker`s run
        method is called.
        :param func: the user-defined function that performs a checking process
        :param callback: an optional callback function to be executed after the func returns.
        :param sleep_time: an optional amount of time in seconds to sleep after the callback returns.
        :param job_name: an optional name for the job. Should be unique as the job is stored in the hashtable. Defaults
        to func.__name__.
        """
        if not job_name:
            job_name = func.__name__

        old_entry = self.job_storage.get(job_name, None)
        new_entry = {'checker': func, 'callback': callback, 'sleep_time': sleep_time}
        sleep_time = old_entry['sleep_time'] if old_entry and old_entry['sleep_time'] and not sleep_time else sleep_time
        new_entry['sleep_time'] = sleep_time

        self.job_storage[job_name] = new_entry
