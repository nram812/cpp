import os
import sys
import numpy as np
import pandas as pd
import xarray as xr
from matplotlib import pyplot as plt
from dateparser import parse


def read_url(month_before_s,url = 'http://ds.data.jma.go.jp/tcc/tcc/products/clisys/mjo/figs/olr0-sst1_1980-2010/rmm8.txt'):
    data = pd.read_table(url, skiprows=2, sep=r'\s+', header=None)
    data.columns = ['year', 'month', 'day', 'RMM1', 'RMM2', 'phase', 'lon', 'amplitude', 'amplitude**2']
    index = pd.to_datetime(data.loc[:, ['year', 'month', 'day']])
    data.index = index
    data = data.loc['1981':, :]
    # obtaining the last two days of the mjo data

    data_pol = data.loc[month_before_s.strftime("%Y-%m-01"):, :]
    return data, data_pol


def filter_month(start_month):
    """
    finds the next month for a given time delta
    """
    start_month = pd.to_datetime(pd.to_datetime(pd.to_datetime(start_month.strftime('%Y-%m-28')) + pd.Timedelta(days =10)).strftime("%Y-%m-01"))
    start_month = (start_month - pd.Timedelta(days =1)).strftime("%Y-%m-%d")
    return start_month


def plot_mjo_cycle(start_month, middle_month, end_month, data_pol, month_before, current_month, previous_month, most_recent_month = True):
    f, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-4, 4)
    ax.set_ylim(-4, 4)
    ax.grid(linestyle=":")
    ax.plot([-4, 4], [-4, 4], color='0.8')
    ax.plot([4, -4], [-4, 4], color='0.8')
    ax.axhline(0, color='0.8')
    ax.axvline(0, color='0.8')
    circ = plt.Circle((0, 0), radius=1, edgecolor='0.8', facecolor='w', zorder=3)
    ax.add_patch(circ)
    start_month = filter_month(start_month)
    middle_month = filter_month(middle_month)
    end_month = filter_month(end_month)
    m1 = data_pol.loc[None:start_month]
    m2 = data_pol.loc[pd.to_datetime(middle_month).strftime("%Y-%m-01"):middle_month]
    m3 = data_pol.loc[pd.to_datetime(end_month).strftime("%Y-%m-01"):]

    plt.title(f"Madden Julian Oscillation phase space ([RMM1, RMM2]) \n for "
              f"{data_pol.index[0].strftime('%d-%B-%Y')} to {data_pol.index[-1].strftime('%d-%B-%Y')}", fontsize=16)
    if most_recent_month:
        ax.plot(m3.RMM1.values, m3.RMM2.values, zorder=4, color='b', linewidth=3)
        for i, row in m3.iterrows():
            ax.text(row.RMM1, row.RMM2, str(row.day), color='k', zorder=5, fontsize=8)

    elif not most_recent_month:
        ax.plot(m1.RMM1.values, m1.RMM2.values, zorder=4, color='r', linewidth=3)
        ax.plot(m2.RMM1.values, m2.RMM2.values, zorder=4, color='g', linewidth=3)
        ax.plot(m3.RMM1.values, m3.RMM2.values, zorder=4, color='b', linewidth=3)
        for i, row in m3.iterrows():
            ax.text(row.RMM1, row.RMM2, str(row.day), color='k', zorder=5, fontsize=8)
        for i, row in m1.iterrows():
            ax.text(row.RMM1, row.RMM2, str(row.day), color='k', zorder=5, fontsize=8)

        for i, row in m2.iterrows():
            ax.text(row.RMM1, row.RMM2, str(row.day), color='k', zorder=5, fontsize=8)
    else:
        ax.plot(m1.RMM1.values, m1.RMM2.values, zorder=4, color='r', linewidth=3)
        ax.plot(m2.RMM1.values, m2.RMM2.values, zorder=4, color='g', linewidth=3)
        for i, row in m1.iterrows():
            ax.text(row.RMM1, row.RMM2, str(row.day), color='k', zorder=5, fontsize=8)

        for i, row in m2.iterrows():
            ax.text(row.RMM1, row.RMM2, str(row.day), color='k', zorder=5, fontsize=8)





    ax.set_ylabel('RMM2')
    ax.set_xlabel('RMM1')

    ax.text(3.5, 0, 'Maritime Continent', horizontalalignment='center', verticalalignment='center', rotation=-90)
    ax.text(-3.5, 0, 'West Hem.\nand Africa', horizontalalignment='center', verticalalignment='center', rotation=90)
    ax.text(0, 3.5, 'Western\nPacific', horizontalalignment='center', verticalalignment='center')
    ax.text(0, -3.5, 'Indian\nOcean', horizontalalignment='center', verticalalignment='center')

    ax.text(-1.5, -3.5, '2', horizontalalignment='center', verticalalignment='center', fontsize=18)
    ax.text(1.5, -3.5, '3', horizontalalignment='center', verticalalignment='center', fontsize=18)
    ax.text(3.5, -1.5, '4', horizontalalignment='center', verticalalignment='center', fontsize=18)
    ax.text(3.5, 1.5, '5', horizontalalignment='center', verticalalignment='center', fontsize=18)
    ax.text(1.5, 3.5, '6', horizontalalignment='center', verticalalignment='center', fontsize=18)
    ax.text(-1.5, 3.5, '7', horizontalalignment='center', verticalalignment='center', fontsize=18)
    ax.text(-3.5, 1.5, '8', horizontalalignment='center', verticalalignment='center', fontsize=18)
    ax.text(-3.5, -1.5, '1', horizontalalignment='center', verticalalignment='center', fontsize=18)

    ax.text(-4.0, -4.45, "{}".format(month_before), color='r', horizontalalignment='center', verticalalignment='center')
    ax.text(-3.0, -4.45, "{}".format(previous_month), color='g', horizontalalignment='center', verticalalignment='center')
    ax.text(-2.0, -4.45, "{}".format(current_month), color='b', horizontalalignment='center', verticalalignment='center')

    # ax.text(-4.0, -4.45, 'September', color='r', horizontalalignment='center', verticalalignment='center')
    # ax.text(-3.0, -4.45, 'October', color='g', horizontalalignment='center', verticalalignment='center')
    # ax.text(-2.0, -4.45, 'November', color='b', horizontalalignment='center', verticalalignment='center')

    f.patch.set_facecolor('white')
    #f.show()
    return f, ax
