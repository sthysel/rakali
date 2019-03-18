""" Exersize rakali tools """

from pathlib import Path

import click
import cv2 as cv

from ..img import Image
from ..testimages import rakali


class OptionConfig(object):
    def __init__(self):
        pass


option_config = click.make_pass_decorator(OptionConfig, ensure=True)


@click.group(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    '-i',
    '--input-file',
    type=click.Path(),
    help='Use file',
    show_default=True,
)
@click.option(
    '-u',
    '--input-url',
    help='Fetch image from URL',
    show_default=True,
)
@click.option(
    '-o',
    '--output-file',
    type=click.Path(),
    default='out.jpg',
    help='Output file',
    show_default=True,
)
@option_config
def cli(config, input_file, input_url, output_file):
    """
    Rakali image tools

    Provide either a input file or a input URL for image source

    """

    config.output_file = Path(output_file).expanduser()

    if input_file and Path(input_file).exists():
        input_file = Path(input_file)
        config.img = Image.from_file(str(input_file))
    elif input_url:
        config.img = Image.from_url(input_url)
    else:
        config.img = rakali


@cli.command()
@option_config
def cvinfo(config):
    """Show OpenCV Build Information"""

    print(cv.getBuildInformation())


@cli.command()
@option_config
def show(config):
    """Show the input image"""

    img: Image = config.img
    img.show()


@cli.command()
@option_config
def grey(config):
    """Show the input image in grey scale"""

    img: Image = config.img
    img.grey().show()


@cli.command()
@option_config
def skeletonize(config):
    """Skeletonize the input image"""

    img: Image = config.img
    img.skeletonize(kernel_size=(3, 3)).show()
    img.write(config.output_file.name)


@click.option(
    '-a',
    '--angle',
    default=45.0,
    help='Rotate image by degrees',
    show_default=True,
)
@cli.command()
@option_config
def rotate(config, angle):
    """Rotate the input image"""

    img: Image = config.img
    img.rotate(angle=float(angle)).show()
    img.write(config.output_file.name)


@click.option(
    '-a',
    '--angle',
    default=45.0,
    help='Rotate image by degrees',
    show_default=True,
)
@cli.command()
@option_config
def rotate_bounded(config, angle):
    """Rotate the input image, keeping bound in place"""

    img: Image = config.img
    img.rotate_bounded(angle=float(angle)).show()
    img.write(config.output_file.name)


@click.option(
    '-w',
    '--width',
    type=click.INT,
    help='Width of resized image',
    show_default=True,
)
@click.option(
    '-h',
    '--height',
    type=click.INT,
    help='Height of resized image',
    show_default=True,
)
@cli.command()
@option_config
def resize(config, width, height):
    """Resize the input image preserving aspect ratio, favoring width"""

    img: Image = config.img
    if width or height:
        img.resize(width=width, height=height).show()
        img.write(config.output_file.name)
    else:
        click.echo('No new width or height specified')
