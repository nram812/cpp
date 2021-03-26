import numpy as np

def format_series_for_bar_plot__(ts_soi, col1 = 'SOI', col2 = 'SOIRM', weekly = False):

    dates = np.array(ts_soi.index.to_pydatetime())
    if weekly is None:
        widths = np.array([(dates[j + 1] - dates[j]).days for j in range(len(dates) - 1)] + [1])
    elif weekly:
        widths = np.array([(dates[j + 1] - dates[j]).days for j in range(len(dates) - 1)] + [7])
    else:
        widths = np.array([(dates[j + 1] - dates[j]).days for j in range(len(dates) - 1)] + [30])
    soi = ts_soi[col1].values.flatten()
    soim = ts_soi[col2].values.flatten()
    return dates, widths, soi, soim
