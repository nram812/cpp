startdate = "2017-01-01"
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter
import pandas as pd
import numpy as np
import os
from monthdelta import monthdelta
import math
import os
import sys
sys.path.append('/nesi/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/lib')
from src import *
input_dirs = r'/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output/time_series'
os.chdir(input_dirs)
brk_dirs = r'/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/seven-station-series-python/output'
main_dirs =r'/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/seven-station-series-python' 
output_dirs = f'{input_dirs}'
ts_all = pd.read_csv(f'{input_dirs}/AllStationMonthly_Anomalies.csv',
                   index_col =0, parse_dates =True)
ts = ts_all.T.mean().apply(lambda a: float("%.2f"%a))
ts.columns = [['Temperature anomaly']]

# Pressure
ts_all['NZT7_Anomally'] =  ts
ts_all.to_excel(f'{input_dirs}/SevenStationSeries.xlsx')
covert_series_to_brick(ts_all,brk_dirs +'/bricks', output_name = 'NZ_T7Anomalies')
ts = ts.truncate(before=startdate)
anoms = ts.values.flatten()

# %%
dates = np.array(ts.index.to_pydatetime())
widths = np.array([(dates[j + 1] - dates[j]).days for j in range(len(dates) - 1)] + [30])
years = YearLocator()
# months  = MonthLocator(bymonth=[1,3,5,7,9,11])
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

y_axis_max = math.ceil(max(anoms))
y_axis_min = math.floor(min(anoms))
ranges = {'well above average': [anoms > 1.20, 'firebrick'],
          'above average': [(anoms >= 0.51) & (anoms <= 1.20), 'darksalmon'],
          'near average': [(anoms >= -0.50) & (anoms <= 0.50), 'lightgrey'],
          'below average': [(anoms >= -1.20) & (anoms <= -0.50), 'steelblue'],
          'well below average': [anoms < -1.20, 'darkblue']}

# %%
# NIWA logo settings
from PIL import Image

im = Image.open(f'{main_dirs}/NIWA_CMYK_Hor.png')
rsize = im.resize((np.array(im.size) / 10).astype(int))  # Use PIL to resize
position = (1120, 540)

# %%
fig, ax = plt.subplots(figsize=(14, 7))
fig.subplots_adjust(bottom=0.15)

for label in ranges:
    rng = ranges[label][0]
    clr = ranges[label][1]

    if True in rng:  # excludes from legend if no data
        ax.bar(dates[rng], anoms[rng], width=widths[rng], label=label, align='center',
               facecolor=clr, alpha=.8, edgecolor='k', lw=1.5)

ax.xaxis.set_minor_locator(months)
ax.xaxis.set_major_locator(years)

# ax.xaxis.set_major_locator(years)
ax.xaxis.set_minor_formatter(mFMT)
ax.xaxis.set_major_formatter(yFMT)
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
ax.set_ylim(y_axis_min, y_axis_max)
ax.set_ylabel(u'Temperature anomaly (\N{DEGREE SIGN}C)', fontsize=14, backgroundcolor="w")
ax.set_xlim(dates[0] - monthdelta(1), dates[-1] + monthdelta(1))

ax.text(0.01,1.02,"NZ 7-station monthly temperature anomalies since {}".format(dates[0].strftime("%b %Y")), fontsize=16, fontweight = 'bold', transform=ax.transAxes)

ax.figure.figimage(rsize,position[0],position[1], alpha=.6, zorder=1)

#ax.figure.figimage(rsize, loc ='upper left', alpha=.6, zorder=1)

######## Label for latest anomaly (top right) ########
u'\N{DEGREE SIGN}'
if round(anoms[-1],1) > 0.0:
    anom_text = u'+{}\N{DEGREE SIGN}C'.format(round(anoms[-1],1)) # adds plus sign to positive anoms
else:
    anom_text = u'{}\N{DEGREE SIGN}C'.format(round(anoms[-1],1))

# writes full month if 5 characters or less. Otherwise abriviate to 3 letters
if len(dates[-1].strftime("%B")) > 5:
    mon_text = "{} value = {}".format(dates[-1].strftime("%b %Y"), anom_text)
else:
    mon_text = "{} value = {}".format(dates[-1].strftime("%B %Y"), anom_text)

ax.text(0.75,1.02,mon_text, fontsize=14, transform=ax.transAxes)
####################################################

leg = ax.legend(loc='upper left', frameon=False)

output_fname = f'NZT7_{dates[-1].strftime("%b%Y")}.png'
fig.savefig(output_fname)
fig.show()
email_title = "7 Station Series Data"
text = f'Here is the Seven Station Series Data for {dates[-1].strftime("%b %Y")}'
print("Emailing the file")
#rcode = os.popen(f'export LC_CTYPE="en_US.UTF-8" && mail -a {input_dirs}/{output_fname} -a {input_dirs}/AllStationMonthly_Anomalies.xlsx -s "##{email_title}" Neelesh.Rampal@niwa.co.nz,Seth.Carrier@niwa.co.nz,John-Mark.Woolley@niwa.co.nz,Ben.Noll@niwa.co.nz', 'w').write(text)

rcode = os.popen(f'export LC_CTYPE="en_US.UTF-8" && mail -a {input_dirs}/{output_fname} -a {input_dirs}/SevenStationSeries.xlsx -s "{email_title}" Neelesh.Rampal@niwa.co.nz,Andrew.Lorrey@niwa.co.nz,Stephen.Stuart@niwa.co.nz,Seth.Carrier@niwa.co.nz,John-Mark.Woolley@niwa.co.nz,Ben.Noll@niwa.co.nz', 'w').write(text)


#rcode = os.popen(f'export LC_CTYPE="en_US.UTF-8" && mail -a {input_dirs}/{output_fname} -a {input_dirs}/SevenStationSeries.xlsx -s "{email_title}" Neelesh.Rampal@niwa.co.nz', 'w').write(text)
