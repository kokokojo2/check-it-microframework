from functools import update_wrapper


class CallbackWrapper:
    def __init__(self, func, checker):
        self.func = func
        self.checker = checker
        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def callback(self, callback_func):
        self.checker.add_job(self.func, callback_func)
        return callback_func


class CheckFunctionsCollectionMixin:
    def __init__(self):
        self.job_storage = {}
        self.wrapper = CallbackWrapper

    # should be used as a decorator
    def check(self, sleep_time=None):
        def check(func):
            self.add_job(func, sleep_time=sleep_time)
            wrapper = self.wrapper(func, self)
            return wrapper
        return check

    def add_job(self, func, callback=None, sleep_time=None, job_name=None):
        if not job_name:
            job_name = func.__name__

        old_entry = self.job_storage.get(job_name, None)
        new_entry = {'checker': func, 'callback': callback, 'sleep_time': sleep_time}
        sleep_time = old_entry['sleep_time'] if old_entry and old_entry['sleep_time'] and not sleep_time else sleep_time
        new_entry['sleep_time'] = sleep_time

        self.job_storage[job_name] = new_entry


