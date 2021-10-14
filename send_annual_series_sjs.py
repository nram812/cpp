#!/usr/bin/python
"""
NAME: send_annual_series_sjs.py
PURPOSE: Plot the annual trend for the NIWA 'Seven-station' temperature series.
AUTHOR: N Rampal, NIWA
--- MODIFICATION HISTORY ---
12.2020: Created script send_annual_series.py.
14.12.2020: S Stuart: Copied script from 
/nesi/project/niwa00018/stuartsj/obs/nz/clidb/seven-station-series-python/send_annual_series.py
to
/nesi/project/niwa00018/stuartsj/obs/nz/clidb/seven-station-series-python/send_annual_series_sjs.py .
Take base directory from current script. Include option to reproduce figure
layout from Mullan's IDL code, including histogram colours, etc. Adjusted text
in email. Adjusted code layout.
"""

import math
from matplotlib import pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np
import os
import pandas as pd
from PIL import Image
from PIL import Image
from scipy.stats import linregress
import sys

# Flags defining behaviour of script.
save_data = True
save_fig = True
send_email = True
debug = True

# Bar formats.
FMT_BAR_1 = 1  
FMT_BAR_2 = 2  # Similar to that from Mullan's IDL code.
fmt_bar = FMT_BAR_2

# Absolute file path.
#dir_base = ('/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series'
#            '-python/')

# Get directory of current script. Works for current structure of git
# repository.
dir_base = os.path.join((os.path.dirname(__file__)), '')

sys.path.append(f'{dir_base}lib/')
from src import *
input_dirs = (f'{dir_base}output/time_series/')
os.chdir(input_dirs)
brk_dirs = f'{dir_base}output/'
main_dirs = f'{dir_base}'
yr_start = 1909
yr_end = 2020
startdate = f'{yr_start}-01-01'

recip_email_all = (
    'Neelesh.Rampal@niwa.co.nz'
    ',Andrew.Lorrey@niwa.co.nz'
    ',Stephen.Stuart@niwa.co.nz'
    ',Seth.Carrier@niwa.co.nz'
    ',John-Mark.Woolley@niwa.co.nz'
    ',Ben.Noll@niwa.co.nz'
    ',Gregor.Macara@niwa.co.nz'
    )

#recip_email_debug = 'Neelesh.Rampal@niwa.co.nz'
recip_email_debug = 'Stephen.Stuart@niwa.co.nz'

if debug:
   recip_email = recip_email_debug  
else:
   recip_email = recip_email_all

# Loading the data
output_dirs = f'{input_dirs}'

ts_all = pd.read_csv(f'{input_dirs}AllStationMonthly_Anomalies.csv',
                     index_col=0, parse_dates=True)

# 14.12.2020: S Stuart: Restrict time series to requested end year.
ts_all = ts_all.iloc[ts_all.index.year <= yr_end]

ts = ts_all.T.mean().apply(lambda a: float("%.2f"%a))
ts.columns = [['Temperature anomaly']]
ts_all['NZT7_Anomally'] = ts

if save_data:
    # Saving the seven_stations_series_to_brick_format
    ts_all.to_excel(f'{input_dirs}Annual_SevenStationSeries.xlsx')

    covert_series_to_brick(
        ts_all, brk_dirs+'bricks', output_name='Annual_NZ_T7Anomalies')

total_months_used = len(ts.loc[ts.index.year==yr_end])

# Computing the slopes of the data.
anoms1 = ts.groupby(ts.index.year).apply(lambda a: np.around(np.mean(a), 2))

# Note that "1909 years was added"
anoms1.loc[1909] = -0.22
anoms1 = anoms1.sort_index()
anoms = anoms1.values.flatten()

f = linregress(anoms1.index.values, anoms1.values.ravel())
slope = '%.2f' % (f.slope * 100)
uncertainty = '%.2f' % (f.stderr * 2 * 100)
values = anoms1.index.values
trend = values * f.slope + f.intercept

# --- Plot the data ---

y_axis_max = math.ceil(max(anoms))
y_axis_min = math.floor(min(anoms))

if fmt_bar == FMT_BAR_1:
    clr_high = 'darksalmon'
    clr_avg = 'lightgrey'
    clr_low = 'steelblue'
    alpha_bar = .8
    lw_bar = 1.5
    wd_bar = 0.8
    lw_trend = 4
    ls_trend = '--'

    ranges = {
        'above average (> 0.5 \N{DEGREE SIGN}C)': [anoms > 0.5, clr_high],
        'near average (-0.5 \N{DEGREE SIGN}C <-> +0.5\N{DEGREE SIGN}C)': [(anoms >= -0.50) & (anoms <= 0.50), clr_avg],
        'below average (< - 0.5 \N{DEGREE SIGN}C)': [anoms < -0.5, clr_low]}
else:
    clr_pos = 'red'
    clr_neg = 'blue'
    alpha_bar = 1.0
    lw_bar = 0
    wd_bar = 0.9
    lw_trend = 3
    ls_trend = '-'

    ranges = {'positive': [anoms >= 0., clr_pos],
              'negative': [anoms < 0., clr_neg]}

if fmt_bar == FMT_BAR_1:
    im = Image.open(f'{main_dirs}/NIWA_CMYK_Hor.png')
    rsize = im.resize((np.array(im.size) / 10).astype(int))  # Use PIL to resize
    position = (1020, 80)

# %%
fig, ax = plt.subplots(figsize=(14, 7))
#fig.subplots_adjust(bottom=0.15)

lbl_trend = (
    f'Trend: {slope}$\pm${uncertainty}'+u'\N{DEGREE SIGN}C/century' + \
    f' ({yr_start}-{yr_end})')

if total_months_used < 12:
    lbl_trend += f' [INCOMPLETE {yr_end} YEAR: {total_months_used} months]'

ax.plot(values, trend, label=lbl_trend, color='k', ls=ls_trend, lw=lw_trend)

for label in ranges:
    rng = ranges[label][0]
    clr = ranges[label][1]

    if True in rng:  # excludes from legend if no data
        
        if fmt_bar == FMT_BAR_1:
            clr_edge = 'k'
        else:
            clr_edge = clr

        ax.bar(anoms1.index.values[rng], anoms[rng], align='center',
               facecolor=clr, alpha=alpha_bar, edgecolor=clr_edge, lw=lw_bar,
               width=wd_bar)

ax.axhline(0, color='k')

labels = ax.get_xminorticklabels()

for label in labels:
    label.set_fontsize(14)
    label.set_rotation(90)

labels = ax.get_xmajorticklabels()

for label in labels:
    label.set_fontsize(18)

labels = ax.get_yticklabels()

for label in labels:
    label.set_fontsize(18)

ax.grid(linestyle=':')
ax.xaxis.grid(True, which='both', linestyle=':')
ax.set_ylim(-1.5, y_axis_max)

ax.set_ylabel(u'Temperature anomaly (\N{DEGREE SIGN}C)', fontsize=16,
              backgroundcolor="w")

ax.set_xticks(np.arange(1910, 2021, 10))
ax.set_xticklabels(['%.0f' % f for f in np.arange(1910,2021,10)])
ax.set_xlim(1905, 2021)#dates[0] - monthdelta(1), dates[-1] + monthdelta(1))

if fmt_bar == FMT_BAR_2:
    ax.tick_params(left=True, right=True, bottom=True, top=True, which='both',
                   direction='in')

    ax.yaxis.set_minor_locator(MultipleLocator(0.1))

    ax.tick_params(which='major', length=8)
    ax.tick_params(which='minor', length=5)

year = yr_end
current_value = anoms1.loc[year]

if current_value >=0.0:
    sign = '+'
else:
    sign =' '

rank = anoms1.sort_values(ascending = False).reset_index()
overall = rank[rank['index'] == yr_end].index.values[0]+1

if str(overall)[-1] == "2":
    ext = "nd"
if str(overall)[-1] == "1":
    ext = "st"
if str(overall)[-1] == "3":
    ext = 'rd'
else:
    ext ='th'
    
titl = ('NZ 7-station annual average temperature, minus 1981-2010 normal'
        ' (adjusted for site changes)')

size_title = 19
ax.set_title(titl, fontsize=size_title, pad=0.6*size_title)

#ax.text(0.01, 1.02, annt, fontsize=16, fontweight='bold',
#        transform=ax.transAxes)

if fmt_bar == FMT_BAR_1:
    ax.figure.figimage(rsize, position[0], position[1], alpha=.6, zorder=1)

ax.set_xlabel('Year', fontsize=16, backgroundcolor="w")
# ax.figure.figimage(rsize, loc ='upper left', alpha=.6, zorder=1)

######## Label for latest anomaly (top right) ########
u'\N{DEGREE SIGN}'

if round(anoms[-1], 1) > 0.0:
    # Add plus sign to positive anoms.
    anom_text = u'+{}\N{DEGREE SIGN}C'.format(round(anoms[-1], 1))
else:
    anom_text = u'{}\N{DEGREE SIGN}C'.format(round(anoms[-1], 1))

# writes full month if 5 characters or less. Otherwise abriviate to 3 letters
# if len(dates[-1].strftime("%B")) > 5:
#    # mon_text = "{} value = {}".format(dates[-1].strftime("%b %Y"), anom_text)
# else:
#    # mon_text = "{} value = {}".format(dates[-1].strftime("%B %Y"), anom_text)

# ax.text(0.75, 1.02, mon_text, fontsize=14, transform=ax.transAxes)
####################################################

leg = ax.legend(loc='upper left', frameon=False, fontsize = 16)
fig.subplots_adjust(bottom=0.08, top=0.94, left=0.07, right=0.98)

#output_fname = f'NZT7_{dates[-1].strftime("%b%Y")}.png'
#fig.savefig(output_fname)
#pth_fig = f'{dir_base}annual_series_{yr_start}-{yr_end}'
pth_fig = f'{dir_base}nzt7_tmean_hist_{yr_start}-{yr_end}'
#pth_fig += '_sjs'  # Debug.
pth_png = pth_fig + '.png'
pth_pdf = pth_fig + '.pdf'
fig.show()

if save_fig:
    fig.savefig(pth_png, dpi=300)
    fig.savefig(pth_pdf)

if send_email:
    email_title = (
        f"7 Station Series Data - Calculated from {total_months_used} months:"
        f" {sign}{'%.2f' % current_value}C ({overall}{ext} warmest)")
        
    text = (
        "Attached are data from the NIWA 'Seven-station' temperature series"
        f" for the {yr_start}-{yr_end} period."
        #f"NZ 7-station annual temperature anomalies since {startdate[:4]}.\n"
        f" The {yr_end} value is {sign}{'%.2f' % current_value}C"
        f" ({overall}{ext} warmest since {startdate[:4]})."
        #"These statistics are for the attached timeseries.\n"
        #"This has been produced in a identical manner to Mullan's Seven"
        #" station series."
        f" The number of months in {yr_end} used for this estimate is"
        f" {total_months_used}."
        " Note: If there are fewer than 12 months, please wait for a"
        " subsequent email.")

    print("Emailing the file")
    cmd = 'export LC_CTYPE="en_US.UTF-8" && mail'
    
    if save_data:
        cmd += (f' -a {dir_base}output/time_series/Annual_SevenStationSeries'
                '.xlsx')

    cmd += f' -a {pth_png}'

    cmd += (f' -a {dir_base}output/bricks/Annual_NZ_T7AnomaliesNZT7_Anomally'
            '.csv')

    cmd += f' -s "{email_title}" {recip_email}'
    rcode = os.popen(cmd, 'w').write(text)
    #rcode = os.popen(cmd, 'w').write('Test text 2.')
    print(f'Status code: {rcode}')

print('Script complete.')
