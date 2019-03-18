#!/usr/bin/env python
"""
Find chessboard pattern in video recording
"""

from pathlib import Path

import cv2 as cv
import time
import sys
from multiprocessing import Process, Queue, cpu_count

from rakali.camera.chessboard import ChessboardFinder
from rakali.video.reader import VideoFrameEnqueuer
from rakali.video.fps import cost

SOURCE = '~/calib/pinhole/l.mkv'
OUT_FOLDER = '~/calib/chessboards/pinhole/left/'


class FindWorker(Process):
    def __init__(self, q, out_path, name):
        super().__init__(name=name)

        self.q = q
        self.out = out_path
        self.finder = ChessboardFinder()

    def run(self):
        print(f'Process {self.name} running')
        q = self.q
        finder = self.finder
        while True:
            ok, frame, frame_number = q.get()
            if ok:
                print(f'{self.name} processing frame {frame_number}')
                if finder.has_chessboard(frame):
                    print(f'{self.name} found chessboard')
                    cv.imwrite(f'{self.out}/{frame_number:05}.jpg', frame)
            else:
                print(f'{self.name} queue empty, done.')
                break


@cost
def find_chessboards_in_file(source, out_folder):
    """
    test each frame in the stream for the presence of a chess-board pattern
    """
    workers = []
    frame_q = Queue(maxsize=200)
    out_path = Path(OUT_FOLDER).expanduser()
    source_path = Path(SOURCE).expanduser()

    enqueuer = VideoFrameEnqueuer(src=str(source_path), q=frame_q)
    with enqueuer:
        for i in range(cpu_count()):
            worker = FindWorker(
                q=enqueuer.q,
                out_path=out_path,
                name=f'FindWorker #{i}',
            )
            workers.append(worker)

        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
        while True:
            if any(proces.is_alive() for proces in workers):
                time.sleep(1)
            else:
                print('All workers done')
                return


if __name__ == '__main__':
    find_chessboards_in_file(source=SOURCE, out_folder=OUT_FOLDER)
    print(f'Processed {SOURCE} in {find_chessboards_in_file.cost}s')
    sys.exit()
