# reading the index
# sa")
df = pd.read_csv(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/trenberth_figures/data/tindex_1981-2010_to_Dec2019.txt', index_col =0,
                   delim_whitespace=True)
def handle_nan(a):
    try:
        return np.int(a)
    except:
        return np.nan

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
        subset[subset > 300] = np.nan
        #subset.values = np.array(subset.values, dtype ='float32')
        corrs = subset.corr(merged_index[index])
        fig, ax = plt.subplots()
        subset.loc["2013":].plot(ax = ax, label =f'Station {index}', color ='b')
        merged_index[index].loc["2013":].plot(ax=ax, color ='r', label =f'{index} Reanalysis (r = {"%.2f" % corrs}')
        ax.legend()
        ax.set_title(f'Comparison of Station Based vs Reanalysis Derived {index} Index')
        fig.savefig(f'/nesi/project/niwa00004/rampaln/CAOA2101/'
                    f'cpp-indices/trenberth_figures/data/validation_figure_{index}.png', dpi =300)
        print(corrs, index)
