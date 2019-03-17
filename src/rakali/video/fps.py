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
        self.start = None
        self.stop = None
        self.frames = 0

    def begin(self):
        """start the timer"""
        self.start = time.perf_counter()
        return self

    def done(self):
        """stop the timer """
        self.end = time.perf_counter()
        self.frames += 1

    def cost(self):
        """
        operation time cost
        """
        return self.end - self.start

    def cost_in_ms(self):
        """
        operation time cost in milliseconds
        """
        return self.cost() * 1000

    def fps(self):
        """the (approximate) frames per second """
        return 1 / self.cost()
