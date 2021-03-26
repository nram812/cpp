
import warnings
warnings.simplefilter(action = "ignore", category = FutureWarning)

import os, sys

import pandas as pd
from io import StringIO, BytesIO
import requests

from datetime import datetime, timedelta

output_dir = '/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/estimate_soi'
# %%
url = "https://data.longpaddock.qld.gov.au/SeasonalClimateOutlook/SouthernOscillationIndex/SOIDataFiles/DailySOI1933-1992Base.txt"
os.environ['HTTP_PROXY'] = ''

# %% [markdown]
# ### Now access the URL via the requests library


# %%
r = requests.get(url)

# %% [markdown]
# ### checks the status code

# %%
if r.status_code != 200:
    print(f"The URL cannot be accessed for some reason, please check the URL:\n{url}")

# %% [markdown]
# ### Now reads the table from the content of the request

# %%
soi = pd.read_csv(url, delim_whitespace=True)#soi = pd.read_table(BytesIO(r.content), sep='\s*', engine='python')


# %%
soi.head()

# %% [markdown]
# ### create the index from year + day of year

# %%
index = [datetime(int(year),1,1) + timedelta(int(day)-1) for year, day in soi.loc[:,['Year','Day']].values]


# %%
soi.index = index


# %%
mslp = soi.copy()


# %%
mslp.head()

# %% [markdown]
# ### check that the last date makes sense

# %%
mslp.tail()

# %% [markdown]
# ### calculates the monthly means from the daily values

# %%
msls_m = mslp.resample('1MS').mean()


# %%
msls_m.tail()

# %% [markdown]
# ### saves to disk in the same folder

# %%
msls_m.tail().to_csv(f'{output_dir}/SOI_estimates.csv')
email_title = "SOI_Estimate"
text = "Automated Script"
rcode = os.popen('export LC_CTYPE="en_US.UTF-8" && mail -a {} -s "{}" Neelesh.Rampal@niwa.co.nz,Ben.Noll@niwa.co.nz,Tristan.Meyers@niwa.co.nz'.format(f'{output_dir}/SOI_estimates.csv', email_title), 'w').write(text)
# %%



# %%




