"""
Find chessboards in image stream and sort frames in folder
"""

from pathlib import Path

import cv2 as cv
import click

from rakali.annotate import add_frame_labels
from rakali.camera.chessboard import ChessboardFinder
from rakali.video import VideoPlayer, go
from rakali.video.reader import VideoStream


def find_chessboards_in_stream(source, out_folder):

    # accommodate the types of sources
    try:
        source = int(source)
        source_path = source
    except ValueError:
        source_path = str(Path(source).expanduser())

    out_path = Path(out_folder).expanduser()
    out_path.mkdir(parents=True, exist_ok=True)

    stream = VideoStream(src=source_path)

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
                display_frame = frame.copy()
                add_frame_labels(display_frame, labels=labels)
                player.show(display_frame)
            else:
                print('No more frames')
                break


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    '-s',
    '--source',
    help='Video source, can be local USB cam (0|1|2..) or IP cam rtsp URL or file',
    default=0,
    show_default=True,
)
@click.option(
    '-o',
    '--output-folder',
    help='Fetch image from URL',
    show_default=True,
)
def cli(source, output_folder):
    """
    test each frame in the stream for the presence of a chess-board pattern
    if found, save to the output folder
    """
    find_chessboards_in_stream(source=source, out_folder=output_folder)
