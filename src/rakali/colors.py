"""
provides useful named colors in BGR
"""

import matplotlib.pyplot as plt
from matplotlib import colors as mcolors


class NoSuchColorException(Exception):
    pass


def _to_bgr(color):
    """convert RGB color to BGR color"""
    r, g, b = [round(x * 255) for x in mcolors.to_rgb(color)]
    return b, g, r


def _set_colors():
    _mcolors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS, **mcolors.XKCD_COLORS)
    return {name.upper().replace(' ', '_'): _to_bgr(color) for name, color in _mcolors.items()}


COLORS = _set_colors()
COLORS['BHP'] = (0, 84, 230)


def get(name):
    """
    Get BGR color
    """
    try:
        return COLORS[name]
    except KeyError:
        raise NoSuchColorException(f'{name} is not a known color')


def get_names():
    """
    Returns list of colors
    """
    return COLORS.keys()


def show_all():
    """
    Show colors sorted by by hue, saturation, value and name.
    """
    colors = dict(mcolors.BASE_COLORS, **mcolors.CSS4_COLORS, **mcolors.XKCD_COLORS)
    by_hsv = sorted((tuple(mcolors.rgb_to_hsv(mcolors.to_rgba(color)[:3])), name) for name, color in colors.items())
    sorted_names = [name for hsv, name in by_hsv]

    n = len(sorted_names)
    ncols = 4
    nrows = n // ncols

    fig, ax = plt.subplots(figsize=(12, 10))

    # Get height and width
    X, Y = fig.get_dpi() * fig.get_size_inches()
    h = Y / (nrows + 1)
    w = X / ncols

    for i, name in enumerate(sorted_names):
        row = i % nrows
        col = i // nrows
        y = Y - (row * h) - h

        xi_line = w * (col + 0.05)
        xf_line = w * (col + 0.25)
        xi_text = w * (col + 0.3)

        ax.text(xi_text, y, name, fontsize=(h * 0.8), horizontalalignment='left', verticalalignment='center')
        ax.hlines(y + h * 0.1, xi_line, xf_line, color=colors[name], linewidth=(h * 0.8))

    ax.set_xlim(0, X)
    ax.set_ylim(0, Y)
    ax.set_axis_off()

    fig.subplots_adjust(left=0, right=1, top=1, bottom=0, hspace=0, wspace=0)
    plt.show()
