import os
import seaborn as sns
from functools import wraps
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.font_manager import FontProperties

sns.set_palette('muted')

CURRENT_PATH = os.path.abspath(os.path.dirname(__file__))
FONT_FILE = 'NotoSansCJKsc-Regular.otf'
FONTS_PATH = os.path.join(CURRENT_PATH, '..', 'fonts', FONT_FILE)
myfont = FontProperties(fname = os.path.abspath(FONTS_PATH))
sns.set(font = myfont.get_family())

HEATMAP_CMAP = sns.diverging_palette(240, 10, as_cmap = True)
MAX_STYLE = 6
FIG_SIZE = (12, 6)

def get_axes(size = FIG_SIZE):
    _, ax = plt.subplots(figsize = size)
    return ax

def reset_legend(axes):
    axes.legend(
        loc='center left',
        bbox_to_anchor=(1, 0.5),
        framealpha = 0,
        prop = myfont,
    )

    return axes

def reset_ticklabels(axes):
    labels = []
    if axes.get_xticklabels():
        labels += axes.get_xticklabels()

    if axes.get_yticklabels():
        labels += axes.get_yticklabels()

    for label in labels:
        label.set_fontproperties(myfont)

    return axes

def fix_axes(axes):
    if not isinstance(axes, Axes):
        return axes

    functions = [reset_ticklabels, reset_legend]

    for func in functions:
        func(axes)
    return axes

def tadpole_axes(fn):
    @wraps(fn)
    def func(*args, **kwargs):
        res = fn(*args, **kwargs)

        if not isinstance(res, tuple):
            return fix_axes(res)
        
        r = tuple()
        for i in res:
            r += (fix_axes(i),)
        
        return r

    return func



def annotate(ax, x, y, space = 5, label = "{:.2f}"):
    """
    """
    va = 'bottom'
    
    if y < 0:
        space *= -1
        va = 'top'

    ax.annotate(
        label.format(y),
        (x, y),
        xytext = (0, space),
        textcoords = "offset points",
        ha = 'center',
        va = va,
    )



def add_bar_annotate(ax, space = 5):
    """
    """
    for rect in ax.patches:
        y_value = rect.get_height()
        x_value = rect.get_x() + rect.get_width() / 2

        annotate(ax, x_value, y_value)
    
    return ax


def add_line_annotate(ax, space = 5):
    """
    """
    for line in ax.lines:
        points = line.get_xydata()
        
        for point in points:
            annotate(ax, point[0], point[1])
    
    return ax


def add_annotate(ax):
    if len(ax.lines) > 0:
        add_line_annotate(ax)
    
    if len(ax.patches) > 0:
        add_bar_annotate(ax)
    
    return ax


