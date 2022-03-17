import urllib.request, urllib.error, urllib.parse
from dateutil import parser as dparser
import pandas as pd
import datetime as dt
import os
import numpy as np
from IPython import get_ipython
import matplotlib as mpl
from matplotlib import pyplot as plt
import pathlib
from monthdelta import monthdelta
import sys
import os
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
from cycler import cycler
import matplotlib.pyplot as plt
from matplotlib.offsetbox import (OffsetImage, TextArea, AnchoredOffsetbox, VPacker)
from PIL import Image


def load_plotting_config__():
    years = YearLocator()
    months = MonthLocator()
    mFMT = DateFormatter('%b')
    yFMT = DateFormatter('\n\n%Y')
    mpl.rcParams['xtick.labelsize'] = 12
    mpl.rcParams['ytick.labelsize'] = 12
    mpl.rcParams['axes.titlesize'] = 14
    mpl.rcParams['xtick.direction'] = 'out'
    mpl.rcParams['ytick.direction'] = 'out'
    mpl.rcParams['xtick.major.size'] = 5
    mpl.rcParams['ytick.major.size'] = 5
    mpl.rcParams['xtick.minor.size'] = 2
    mpl.rcParams['lines.linewidth'] = 2
    mpl.rcParams['lines.linestyle'] = '--'
    mpl.rcParams['axes.prop_cycle'] = cycler(color=['r', 'g', 'b', 'y'])
    mpl.rcParams['font.family'] = 'sans-serif'
    mpl.rcParams['axes.labelsize'] ='medium'
    mpl.rcParams['axes.formatter.use_mathtext'] = True
    # mpl.rcParams['font.weight'] = 'bold'
    mpl.rcParams['figure.titleweight'] = 'bold'
    mpl.rcParams['figure.titlesize'] = 20
    return years, months, mFMT, yFMT


def plot_data(dates, soi, widths, soim, months, output_path ="/nesi/project/niwa00004/rampaln/CPP_indices/SOI/figures/",
              cei = True, var_name = 'SOI', var_2 ='3-mth mean', title = True, label_bool = None,
              loc = "lower right", ylim = (-100,100), period1 = -3, period2 =-1, periodicity = 'D',subplot_kwargs = dict(),
              figsize = (14,10), imagepath = None
              ):
    """
    
    :param dates: 
    :param soi: 
    :param widths: 
    :param soim: 
    :param months: 
    :param output_path: 
    :param cei: 
    :param var_name: 
    :param var_2: 
    :param title: 
    :param label_bool: 
    :param loc: 
    :param ylim: 
    :param period1: the period to produce an average comment over
    :param period2: the second period to compute an average over.
    :return: 
    """
    fig, ax = plt.subplots(figsize=figsize,subplot_kw=subplot_kwargs)
    fig.subplots_adjust(bottom=0.15)
    if cei:
        ax.bar(dates[soi >= 0], soi[soi >= 0], width=widths[soi >= 0], facecolor='coral', alpha=.5, edgecolor='k',
               lw=2)
        ax.bar(dates[soi < 0], soi[soi < 0], width=widths[soi < 0], facecolor='steelblue', alpha=.5, edgecolor='k', lw=2)
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))
        ax.tick_params(axis="x", which="major", pad=12)
    else:

        ax.bar(dates[soi >= 0], soi[soi >= 0], width=widths[soi >= 0], facecolor='steelblue', alpha=.8, edgecolor='k', lw=2)
        ax.bar(dates[soi < 0], soi[soi < 0], width=widths[soi < 0], facecolor='coral', alpha=.8, edgecolor='k', lw=2)
        if not cei:
            ax.plot(dates, soim, lw=3, color='k', label=var_2)
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(DateFormatter('%b %Y'))

        ax.tick_params(axis="x", which="major", pad=12)
        ax.xaxis.grid(False)
        ax.yaxis.grid(False)
    ax.axhline(0, color='k')

    labels = ax.get_xmajorticklabels()

    for i, label in enumerate(labels):
        label.set_rotation(90)
        label.set_fontsize(12)
    ax.grid('off')
    # ax.grid(linestyle=':')
    # ax.xaxis.grid(True, which='both', linestyle=':')
    ax.legend(loc=3, fancybox=True)
    ax.set_ylim(ylim)
    ax.set_ylabel(f'Monthly {var_name}', fontsize=14, backgroundcolor="w")


    # Definitely the title
    ax.text(0.01, 1.02, f"{var_name}", fontsize=24, fontweight='bold', transform=ax.transAxes)
    ax.set_xlim(dates[0] - monthdelta(1), dates[-1] + monthdelta(1))
    if periodicity == 'M':
        textBm = "{:%b %Y} = {:+3.1f}".format(dates[-period1], soi[-period1])
        textBs = "%s to %s = %+3.1f" % (dates[-period2].strftime("%b %Y"), dates[-period1].strftime("%b %Y"), soi[-period2:-period1].mean())
    else:

        textBm = "{:%b %d %Y } = {:+3.1f}".format(dates[-period1], soi[-period1])
        textBs = "%s to %s = %+3.1f" % (
        dates[-period2].strftime("%b %d %Y"), dates[-period1].strftime("%b %d %Y"), soi[-period2:-period1].mean())

    if label_bool is None:
        if imagepath is not None:
            ax = create_watermark(fig,
                                  label=None, ax=ax, alpha=1, loc=loc, imagePath=imagepath)
        else:
            ax = create_watermark(fig,
                                  label=None, ax=ax, alpha=1, loc=loc)
    else:
        if imagepath is not None:
            ax = create_watermark(fig,
                                  label=None, ax=ax, alpha=1, loc=loc, imagePath=imagepath)
        else:
            ax = create_watermark(fig,
                             label="Latest values: {}, {}".format(textBm, textBs), ax=ax, alpha=1, loc = loc)


    if cei:
        if title:
            ax.text(0.25, 1.02, "Latest values: {}, {}".format(textBm, textBs), fontsize=16, transform=ax.transAxes);
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if not os.path.exists(f'{output_path}/real_time_monthly_NIWA_SOI_1941_2010_updated_{dates[-1].strftime("%Y-%m")}.png'):
            return fig,ax, f'{output_path}/real_time_monthly_NIWA_SOI_1941_2010_updated_{dates[-1].strftime("%Y-%m")}.png',True,textBm, textBs
        else:
            return fig,ax,f'{output_path}/real_time_monthly_NIWA_SOI_1941_2010_updated_{dates[-1].strftime("%Y-%m")}.png', False,textBm, textBs
    else:
        ax.text(0.25, 1.02, "Latest values: {}, {}".format(textBm, textBs), fontsize=16, transform=ax.transAxes);
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        if not os.path.exists(
                f'{output_path}/real_time_monthly_NIWA_SOI_1941_2010_updated_{dates[-1].strftime("%Y-%m")}.png'):
            fig.savefig(f'{output_path}/real_time_monthly_NIWA_SOI_1941_2010_updated_{dates[-1].strftime("%Y-%m")}.png',
                        dpi=200)
            return fig,ax, f'{output_path}/real_time_monthly_NIWA_SOI_1941_2010_updated_{dates[-1].strftime("%Y-%m")}.png', True, textBm, textBs
        else:
            return fig,ax, f'{output_path}/real_time_monthly_NIWA_SOI_1941_2010_updated_{dates[-1].strftime("%Y-%m")}.png', False,textBm, textBs


def create_watermark(fig, imagePath ='./lib/NIWA_CMYK_Hor.png',
                     label = 'Climate Present and Past', ax=None, alpha=0.5, loc = "upper left"):
    img = Image.open(imagePath)
    width, height = ax.figure.get_size_inches()*fig.dpi
    wm_width = np.int(width/4) # make the watermark 1/4 of the figure size
    scaling = (wm_width / np.float(img.size[0]))
    wm_height = np.int(float(img.size[1])*float(scaling))
    img = img.resize((wm_width, wm_height), Image.ANTIALIAS)
    print(label)
    if label is None:
        imagebox = OffsetImage(img, alpha=alpha, zoom=0.4)
        packer = VPacker(children=[imagebox], mode='fixed', pad=0.7, sep=0.3, align='center')
    else:
        imagebox = OffsetImage(img, alpha=alpha, zoom=0.4)
        packer = VPacker(children=[imagebox], mode='fixed', pad=0.7, sep=0.3, align='center')
    ao = AnchoredOffsetbox(loc, pad=0.6, borderpad=0.6, child=packer)
    ao.patch.set_alpha(0)
    ax.add_artist(ao)
    return ax


def add_reference(ax, fontsize,
                  text, top_corner=0.97, separation=0.03,
                  data_source="http://www.niwa.co.nz/CPPdata",
                  ref="Ref: Gergis & Fowler, 2005; DOI: 10.1002/joc.1202"):
    ax.text(0.01, top_corner, f"{ref}", fontsize=fontsize, fontweight='normal', transform=ax.transAxes)
    ax.text(0.01, top_corner - separation, f"Data Sources: See {data_source}", fontsize=fontsize, fontweight='normal',
            transform=ax.transAxes)
    multiplier = 2.0
    for text_ in text:
        ax.text(0.01, top_corner - multiplier * separation, "{}".format(text_), fontweight='bold', fontsize=fontsize,
                transform=ax.transAxes)
        multiplier +=1
    return ax
