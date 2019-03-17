#! /usr/bin/env python
"""
Find chessboards in image stream and sort frames in folder
"""

from pathlib import Path

import cv2 as cv

from rakali.annotate import add_frame_labels
from rakali.camera.chessboard import ChessboardFinder
from rakali.video import VideoPlayer, go
from rakali.video.reader import VideoFileProducer

SOURCE = '~/calib/pin/l.mkv'
OUT_FOLDER = '~/calib/chessboards/pinhole/left/'


def find_chessboards_in_stream(source, out_folder):
    """
    test each frame in the stream for the presence of a chess-board pattern
    """
    out_path = Path(OUT_FOLDER).expanduser()
    source_path = Path(SOURCE).expanduser()

    stream = VideoFileProducer(src=str(source_path))

    finder = ChessboardFinder()
    player = VideoPlayer(stream=stream)

    with player, stream:
        count = 0
        while go():
            ok, frame = stream.read()
            labels = [f'FPS {stream.read.cost:.6f}s']
            if ok:
                if finder.has_chessboard(frame):
                    cv.imwrite(f'{out_path}/{count:05}.jpg', frame)
                    count += 1
                    labels.append('CHESSBOARD')
                else:
                    labels.append('NO CHESSBOARD FOR YOU')

                labels.append(f'find chessboard cost: {finder.has_chessboard.cost:.3f}s')
                add_frame_labels(frame, labels=labels)
                player.show(frame)
            else:
                print('No more frames')
                break


SOURCE = '~/calib/pin/l.mkv'
OUT_FOLDER = '~/calib/chessboards/pinhole/left/'

find_chessboards_in_stream(source=SOURCE, out_folder=OUT_FOLDER)
