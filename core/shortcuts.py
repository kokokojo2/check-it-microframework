from functools import update_wrapper


class Statuses:
    SUCCESS = 0
    FAILURE = 1
    TRY_AGAIN = 2


class StatusCallbackWrapper:
    def __init__(self, func, checker):
        self.func = func
        self.checker = checker
        self.callback_per_status = {}

        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def _get_universal_callback(self):
        def universal_callback(check_result):
            try:
                self.callback_per_status.get(check_result[0], None)(check_result)
            except KeyError:
                pass

        return universal_callback

    def callback(self, status, sleep_time=None):
        def wrapper(callback_func):
            self.callback_per_status[status] = callback_func
            self.checker.add_job(self.func, callback=self._get_universal_callback(), sleep_time=sleep_time)
            return callback_func
        return wrapper

    def success(self, sleep_time=None):
        return self.callback(Statuses.SUCCESS, sleep_time=sleep_time)

    def failure(self, sleep_time=None):
        return self.callback(Statuses.FAILURE, sleep_time=sleep_time)

    def try_again(self, sleep_time=None):
        return self.callback(Statuses.TRY_AGAIN, sleep_time=sleep_time)
