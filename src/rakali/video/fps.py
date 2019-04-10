import time

import functools


def cost(func):
    @functools.wraps(func)
    def wrapper_timer(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        wrapper_timer.cost = end_time - start_time
        wrapper_timer.fps = 1 / (end_time - start_time)
        return value

    wrapper_timer.cost = 0
    return wrapper_timer


class FPS:
    """
    Keeps track of time spend doing various processing on frames
    """

    def __init__(self):
        self._start = None
        self._stop = None
        self._frames = 0

    def start(self):
        """start the timer"""
        self._start = time.perf_counter()
        return self

    def stop(self):
        """stop the timer """
        self._stop = time.perf_counter()
        self._frames += 1

    def cost(self):
        """
        operation time cost
        """
        return self._stop - self._start

    def cost_in_ms(self):
        """
        operation time cost in milliseconds
        """
        return self.cost() * 1000

    def fps(self):
        """the (approximate) frames per second """
        return 1 / self.cost()
