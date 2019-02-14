""" Exersize rakali tools """

from pathlib import Path

import click

from ..img import Image, ImageSize


class OptionConfig(object):
    def __init__(self):
        pass


option_config = click.make_pass_decorator(OptionConfig, ensure=True)


@click.group(context_settings=dict(max_content_width=120))
@click.version_option()
@click.option(
    '-i',
    '--input-file',
    type=click.Path(exists=True),
    default=Path('.'),
    help='Use file',
    show_default=True,
)
@option_config
def cli(config, input_file):
    config.file = input_file


@cli.command()
@option_config
def skeletonize(config):
    img = Image.fromfile(config.file)
    img.show()
    img.skeletonize(kernel_size=(3, 3))
    img.show()


@cli.command()
@option_config
def rotate(config):
    img: Image = Image.fromfile(config.file)
    img.rotate(angle=30).show()
