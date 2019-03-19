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


def find_chessboards_in_stream(source, chessboard_size, out_folder):
    # accommodate the types of sources
    if source.find('rtsp') >= 0:
        source_path = source
    else:
        try:
            source = int(source)
            source_path = source
        except ValueError:
            source_path = str(Path(source).expanduser())
    print(source_path)

    out_path = Path(out_folder).expanduser()
    out_path.mkdir(parents=True, exist_ok=True)

    stream = VideoStream(src=source_path)

    finder = ChessboardFinder(chessboard_size)
    player = VideoPlayer(stream=stream)

    with player, stream:
        count = 0
        while go():
            ok, frame = stream.read()
            labels = [f'FPS {stream.read.cost:.6f}s']
            if ok:
                display_frame = frame.copy()
                has_corners, corners = finder.corners(frame)
                if has_corners:
                    cv.imwrite(f'{out_path}/{count:05}.jpg', frame)
                    count += 1
                    labels.append('CHESSBOARD')
                    finder.draw(display_frame, corners)
                else:
                    labels.append('NO CHESSBOARD FOR YOU')

                labels.append(f'find chessboard cost: {finder.has_chessboard.cost:.3f}s')
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
    default="http://axis-lab/axis-cgi/mjpg/video.cgi?&camera=1",
    show_default=True,
)
@click.option(
    '-o',
    '--output-folder',
    help='Fetch image from URL',
    default='~/rakali/chessboards/',
    show_default=True,
)
@click.option(
    '--chessboard-rows',
    help='Chessboard rows',
    default=9,
    show_default=True,
)
@click.option(
    '--chessboard-columns',
    help='Chessboard columns',
    default=6,
    show_default=True,
)
def cli(source, output_folder, chessboard_rows, chessboard_columns):
    """
    Test each frame in the stream for the presence of a chess-board pattern.
    If found, save to the output folder
    """
    size = (chessboard_columns, chessboard_rows)
    find_chessboards_in_stream(
        source=source,
        chessboard_size=size,
        out_folder=output_folder,
    )
