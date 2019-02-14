""" Exersize rakali tools """

from pathlib import Path

import click

from ..img import Image


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

    if input_file and input_file.exists():
        input_file = Path(input_file)
        config.img = Image.from_file(str(input_file))
    elif input_url:
        print(input_url)
        config.img = Image.from_url(input_url)


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
    default=90.0,
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
