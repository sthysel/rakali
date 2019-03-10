import time


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
        self.start = time.time()
        return self

    def done(self):
        """stop the timer """
        self.end = time.time()
        self.frames += 1

    def cost(self):
        """
        operation time cost
        """
        return self.end - self.start

    def fps(self):
        """the (approximate) frames per second """
        return 1 / self.cost()
