# This script is for plotting the annual trend for the seven station series
startdate = "1909-01-01"
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import math
import os

import sys
sys.path.append('/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/lib')
from src import *
input_dirs = r'/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/time_series'
os.chdir(input_dirs)
brk_dirs = r'/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output'
main_dirs =r'/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/seven-station-series-python'

# Loading the data
output_dirs = f'{input_dirs}'
ts_all = pd.read_csv(f'{input_dirs}/AllStationMonthly_Anomalies.csv',
                   index_col =0, parse_dates =True)
ts = ts_all.T.mean().apply(lambda a: float("%.2f"%a))
ts.columns = [['Temperature anomaly']]
ts_all['NZT7_Anomally'] =  ts

# Saving the seven_stations_series_to_brick_format
ts_all.to_excel(f'{input_dirs}/Annual_SevenStationSeries.xlsx')
covert_series_to_brick(ts_all,brk_dirs +'/bricks', output_name = 'Annual_NZ_T7Anomalies')

total_months_used = len(ts.loc[ts.index.year == 2020])
# Computing the slopes of the data.
anoms1 = ts.groupby(ts.index.year).apply(lambda a: np.around(np.mean(a),2))

# Note that "1909 years was added"
anoms1.loc[1909] =-0.22
anoms1 = anoms1.sort_index()
anoms = anoms1.values.flatten()

from scipy.stats import linregress
f = linregress(anoms1.index.values, anoms1.values.ravel())
slope = '%.2f' % (f.slope * 100)
uncertainty = '%.2f' % (f.stderr * 2 * 100)
values = anoms1.index.values
trend = values * f.slope + f.intercept


# Plotting the data



y_axis_max = math.ceil(max(anoms))
y_axis_min = math.floor(min(anoms))
ranges = {'above average (> 0.5 \N{DEGREE SIGN}C)': [anoms > 0.5, 'darksalmon'],
          'near average (-0.5 \N{DEGREE SIGN}C <-> +0.5\N{DEGREE SIGN}C)': [(anoms >= -0.50) & (anoms <= 0.50), 'lightgrey'],
          'below average (< - 0.5 \N{DEGREE SIGN}C)': [anoms < -0.5, 'steelblue']}
from PIL import Image
from PIL import Image

im = Image.open(f'{main_dirs}/NIWA_CMYK_Hor.png')
rsize = im.resize((np.array(im.size) / 10).astype(int))  # Use PIL to resize
position = (1020, 80)

# %%
current_date = '2020'
fig, ax = plt.subplots(figsize=(14, 7))
fig.subplots_adjust(bottom=0.15)
ax.plot(values, trend,
        label = f'Trend: {slope}$\pm${uncertainty}'+u'\N{DEGREE SIGN}C/century' + f'  {startdate[0:4]} - {current_date}',
        color = 'k', ls ='--', lw = 4)

for label in ranges:
    rng = ranges[label][0]
    clr = ranges[label][1]

    if True in rng:  # excludes from legend if no data
        ax.bar(anoms1.index.values[rng], anoms[rng], align='center',
               facecolor=clr, alpha=.8, edgecolor='k', lw=1.5)

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
ax.set_ylabel(u'Temperature anomaly (\N{DEGREE SIGN}C)', fontsize=16, backgroundcolor="w")
ax.set_xticks(np.arange(1910,2021,10))
ax.set_xticklabels(['%.0f' % f for f in np.arange(1910,2021,10)])
ax.set_xlim(1905,2021)#dates[0] - monthdelta(1), dates[-1] + monthdelta(1))
year = 2020
current_value = anoms1.loc[year]
if current_value >=0.0:
    sign = '+'
else:
    sign =' '
rank = anoms1.sort_values(ascending = False).reset_index()
overall = rank[rank['index'] ==2020].index.values[0]+1
if str(overall)[-1] == "2":
    ext = "nd"
if str(overall)[-1] == "1":
    ext = "st"
if str(overall)[-1] == "3":
    ext = 'rd'
else:
    ext ='th'
ax.text(0.01, 1.02, f"NZ 7-station annual temperature anomalies since {startdate[:4]}, 2020 Value : {sign}{'%.2f' % current_value} ({overall}" +"$^{" + f'{ext}'+"}$ Hottest on Record)",
        fontsize=16, fontweight='bold', transform=ax.transAxes)

ax.figure.figimage(rsize, position[0], position[1], alpha=.6, zorder=1)
ax.set_xlabel('Year', fontsize=16, backgroundcolor="w")
# ax.figure.figimage(rsize, loc ='upper left', alpha=.6, zorder=1)

######## Label for latest anomaly (top right) ########
u'\N{DEGREE SIGN}'
if round(anoms[-1], 1) > 0.0:
    anom_text = u'+{}\N{DEGREE SIGN}C'.format(round(anoms[-1], 1))  # adds plus sign to positive anoms
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

#output_fname = f'NZT7_{dates[-1].strftime("%b%Y")}.png'
#fig.savefig(output_fname)

fig.savefig('/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/annual_series.png')
fig.show()
email_title = f"7 Station Series Data - Calculated from {total_months_used} months ({sign}{'%.2f' % current_value} ({overall}{ext} Hottest on Record)"
text = f'Here is the Seven Station Series Data for 2020 \\n' \
       f' The attacted timeseries are for which these statistics are produced for. \\n' \
       f' Note: This has been produced in a identical manner to Mullans seven station series ' \
       f' The number of months used for this estimate is {total_months_used}, Note if there are fewer 12 months please wait for a subsequent email'
print("Emailing the file")

rcode = os.popen(f'export LC_CTYPE="en_US.UTF-8" && mail -a /nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/time_series/Annual_SevenStationSeries.xlsx -a /nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/annual_series.png -a /nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/bricks/Annual_NZ_T7AnomaliesNZT7_Anomally.csv -s "{email_title}" Neelesh.Rampal@niwa.co.nz,Andrew.Lorrey@niwa.co.nz,Stephen.Stuart@niwa.co.nz,Seth.Carrier@niwa.co.nz,John-Mark.Woolley@niwa.co.nz,Ben.Noll@niwa.co.nz,Gregor.Macara@niwa.co.nz',
                 'w').write(text)

