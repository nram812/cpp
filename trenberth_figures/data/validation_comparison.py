# reading the index
# sa")
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
df = pd.read_csv(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/trenberth_figures/data/tindex_1981-2010_to_Dec2019.txt', index_col =0,
                   delim_whitespace=True)
merged_index = pd.read_csv(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/trenberth_figures/data/updated_trenberth_index.csv',
                           index_col =0, parse_dates = True)
def handle_nan(a):
    try:
        return np.int(a)
    except:
        return np.nan
merged_data = []
for index in df.index.unique()[1:]:
    subset = df.loc[index]
    # remove the last column
    subset = subset[subset.columns[:-1]]
    # melt the data
    subset = pd.melt(subset, id_vars=['YEAR'])
    subset.index = subset[['YEAR','variable']].T.apply(lambda a : pd.to_datetime(f'{int(a[0])}-{a[1]}-01',
                                                                                 format="%Y-%b-01"))
    subset = subset.sort_index()['value']
    subset = subset.loc[:]
    subset =pd.DataFrame(subset)
    subset.columns = [index]
    if index in merged_index.columns:
        #subset = subset.loc["2000":]
        subset = subset.T.apply(handle_nan)
        subset[abs(subset) > 300] = np.nan
        #subset.values = np.array(subset.values, dtype ='float32')
        corrs = subset.corr(merged_index[index])
        error = abs((subset - merged_index[index]))
        intersection = subset.index.intersection(merged_index[index].index)
        diff = subset.index.difference(merged_index[index].index)
        merged_dset = pd.concat([subset.loc[diff], merged_index[index]])
        merged_dset.name = merged_index[index].name
        merged_data.append(merged_dset.loc["1940":])

        print(corrs, index, error.mean(), subset.std())
        fig, ax = plt.subplots()
        subset.loc["1979":].plot(ax = ax, label =f'Station {index}', color ='b')
        merged_index[index].loc["1979":].plot(ax=ax, color ='r', label =f'{index} Reanalysis (r = {"%.2f" % corrs}')
        ax.legend()
        ax.set_title(f'Comparison of Station Based vs Reanalysis Derived {index} Index')
        fig.savefig(f'/nesi/project/niwa00004/rampaln/CAOA2101/'
                    f'cpp-indices/trenberth_figures/data/validation_figure_{index}.png', dpi =300)
        print(corrs, index)
merged = pd.DataFrame(data = merged_data).T
fig, ax = plt.subplots()
merged.loc["1940":"1950"].plot(ax =ax)
fig.show()