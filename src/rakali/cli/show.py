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
    help='Use file',
    show_default=True,
)
@option_config
def cli(config, input_file):
    config.file = Path(input_file)


@cli.command()
@option_config
def skeletonize(config):
    path: Path = config.file.expanduser()

    img = Image.fromfile(str(path))
    img.show()

    img.skeletonize(kernel_size=(3, 3))
    img.show()

    img.write(f'skeletonized-{path.name}')


@cli.command()
@option_config
def rotate(config):
    img: Image = Image.fromfile(config.file)
    img.rotate(angle=30).show()
