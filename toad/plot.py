import numpy as np
import pandas as pd
from sklearn.metrics import roc_curve

from .tadpole import tadpole
from .tadpole.utils import HEATMAP_CMAP, add_annotate
from .utils import unpack_tuple, generate_str


def badrate_plot(frame, x = None, target = 'target', by = None,
                freq = None, format = None, return_counts = False,
                return_proportion = False, return_frame = False):
    """plot for badrate

    Args:
        frame (DataFrame)
        x (str): column in frame that will be used as x axis
        target (str): target column in frame
        by (str): column in frame that will be calculated badrate by it
        freq (str): offset aliases string by pandas
                    http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
        format (str): format string for time
        return_counts (bool): if need return counts plot
        return_frame (bool): if need return frame

    Returns:
        Axes: badrate plot
        Axes: counts plot
        Axes: proportion plot
        Dataframe: grouping detail data
    """
    frame = frame.copy()
    markers = True

    if not isinstance(target, str):
        temp_name = generate_str()
        frame[temp_name] = target
        target = temp_name

    grouper = x
    if freq is not None:
        frame.loc[:, x] = pd.to_datetime(frame[x], format = format)
        grouper = pd.Grouper(key = x, freq = freq)

    if by is not None:
        grouper = [by, grouper]

        styles_count = frame[by].nunique()
        if styles_count > MAX_STYLE:
            markers = ['o'] * styles_count

    group = frame.groupby(grouper)
    table = group[target].agg(['sum', 'count']).reset_index()
    table['badrate'] = table['sum'] / table['count']


    rate_plot = tadpole.lineplot(
        x = x,
        y = 'badrate',
        hue = by,
        style = by,
        data = table,
        legend = 'full',
        markers = markers,
        dashes = False,
    )
    res = (rate_plot,)

    if return_counts:
        count_plot = tadpole.barplot(
            x = x,
            y = 'count',
            hue = by,
            data = table,
        )
        res += (count_plot,)


    if return_proportion:
        table['prop'] = 0
        for v in table[x].unique():
            mask = (table[x] == v)
            table.loc[mask, 'prop'] = table[mask]['count'] / table[mask]['count'].sum()

        prop_plot = tadpole.barplot(
            x = x,
            y = 'prop',
            hue = by,
            data = table,
        )
        res += (prop_plot,)


    if return_frame:
        res += (table,)

    return unpack_tuple(res)


def corr_plot(frame, figure_size = (20, 15)):
    """plot for correlation

    Args:
        frame (DataFrame): frame to draw plot
    Returns:
        Axes
    """
    corr = frame.corr()

    mask = np.zeros_like(corr, dtype = np.bool)
    mask[np.triu_indices_from(mask)] = True

    map_plot = tadpole.heatmap(
        corr,
        mask = mask,
        cmap = HEATMAP_CMAP,
        vmax = 1,
        vmin = -1,
        center = 0,
        square = True,
        cbar_kws = {"shrink": .5},
        linewidths = .5,
        annot = True,
        fmt = '.2f',
        figure_size = figure_size,
    )

    return map_plot


def proportion_plot(x = None, keys = None):
    """plot for proportion

    Args:
        x (Series|list): series or list of series data for plot
        keys (str|list): keys for each data

    Returns:
        Axes
    """
    if not isinstance(x, list):
        x = [x]

    if keys is None:
        keys = [
            x[ix].name
            if hasattr(x[ix], 'name') and x[ix].name is not None
            else ix
            for ix in range(len(x))
        ]
    elif isinstance(keys, str):
        keys = [keys]

    x = map(pd.Series, x)
    data = pd.concat(x, keys = keys, names = ['keys']).reset_index()
    data = data.rename(columns = {data.columns[2]: 'value'})

    prop_data = data.groupby('keys')['value'].value_counts(
        normalize = True,
        dropna = False,
    ).rename('proportion').reset_index()

    prop_plot = tadpole.barplot(
        x = 'value',
        y = 'proportion',
        hue = 'keys',
        data = prop_data,
    )

    return prop_plot


def roc_plot(score, target):
    """plot for roc

    Args:
        score (array-like): predicted score
        target (array-like): true target

    Returns:
        Axes
    """

    fpr, tpr, thresholds = roc_curve(target, score)

    ax = tadpole.lineplot(
        x = fpr,
        y = tpr,
    )

    ax = ax.plot([0, 1], [0, 1], color = 'red', linestyle = '--')

    return ax


def bin_plot(frame, x = None, target = 'target'):
    """plot for bins
    """
    group = frame.groupby(x)
    
    table = group[target].agg(['sum', 'count']).reset_index()
    table['badrate'] = table['sum'] / table['count']
    table['prop'] = table['count'] / table['count'].sum()

    prop_ax = tadpole.barplot(
        x = x,
        y = 'prop',
        data = table,
        color = '#82C6E2',
    )

    prop_ax = add_annotate(prop_ax)

    badrate_ax = prop_ax.twinx()
    badrate_ax.grid(False)

    badrate_ax = tadpole.lineplot(
        x = x,
        y = 'badrate',
        data = table,
        color = '#D65F5F',
        ax = badrate_ax,
    )
    
    badrate_ax = add_annotate(badrate_ax)

    return prop_ax


    