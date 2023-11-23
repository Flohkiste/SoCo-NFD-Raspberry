import time
import threading


class MyTimer:
    def __init__(self, duration, function):
        self.start_time = time.time()
        self.duration = duration
        self.function = function
        self.timer = threading.Timer(duration, function)

    def start(self):
        self.timer.start()

    def cancel(self):
        self.timer.cancel()

    def time_left(self):
        elapsed_time = time.time() - self.start_time
        return max(0, self.duration - elapsed_time)

    def elapsed_time(self):
        return time.time() - self.start_time
