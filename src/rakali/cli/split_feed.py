"""
split stereo feed into separate feeds
"""

import click

from rakali.video.reader import VideoFile
from rakali.video.writer import VideoWriter


@click.command(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    '-s',
    '--source',
    help='Stereo video source file to split',
    default='in.avi',
    show_default=True,
)
@click.option(
    '-l',
    '--left-name',
    help='Left camera video name',
    default='left_eye_out.avi',
    show_default=True,
)
@click.option(
    '-r',
    '--right-name',
    help='Right camera video name',
    default='right_eye_out.avi',
    show_default=True,
)
@click.option(
    '--fps',
    help='Frames per second rate for output file',
    default=12.5,
    show_default=True,
)
def cli(source, left_name, right_name, fps):
    """
    Split source stereo recording into left and right camera views
    """

    print(f'Decomposing stereo video file {source} into {left_name}, {right_name}')
    l_writer = VideoWriter(file_name=left_name, fps=fps)
    r_writer = VideoWriter(file_name=right_name, fps=fps)

    infile = VideoFile(source)

    print('Calculate size...')
    ok, frame = infile.read()
    if ok:
        h, w = frame.shape[:2]
        hw = int(w / 2)

    print('Splitting....')
    while True:
        ok, frame = infile.read()
        if ok:
            left = frame[0:h, 0:hw]
            right = frame[0:h, hw:w]

            l_writer.write(left)
            r_writer.write(right)
        else:
            break
    print('Done.')
