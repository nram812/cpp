from scipy.stats import linregress
f = linregress(index['SOI'],ts_soi['soi'])

z1 = index['SOI'].apply(lambda a: a *f.slope + f.intercept)
fig, ax = plt.subplots()
z1.loc["2018":].plot(ax = ax, color ='b', label = 'SOI Reanalysis')
ts_soi['soi'].loc["2018":].plot(ax = ax, color ='r', label ='BOM SOI')
(index['Nino 3.4']*-1).loc["2018":].plot(ax = ax, color ='k', label = '-1 * Nino 3.4')
fig.show()
index['SOI'].corr(ts_soi['soi'])
fig, ax = plt.subplots()
index['SOI'].loc["2012":].plot(ax = ax)
ts_soi['soi'].loc["2012":].plot(ax = ax, color='b')
fig.show()


fig, ax = plt.subplots()
index['Nino 3.4'].loc["2018":].plot( ax = ax)
nino['anoms'].loc["2018":].plot(ax = ax, color ='b')
fig.show()

fig, ax = plt.subplots()


def organize_cei(clim_start=clim_start, clim_end=clim_end):
    # --- Here is the analysis for the CEI ---
    tahitidf = get_BOM_MSLP(station='tahiti')
    darwindf = get_BOM_MSLP(station='darwin')
    # Process the soi and other fields
    index = pd.read_csv(r'./indices/data/monthly_index.csv',
                        index_col=0, parse_dates=True)
    index['soi3m'] = index['SOI'].rolling(window =3).mean()
    index['soi'] = index['SOI']
    dates = index.index
    ts_soi, dates, soi = compute_soi(tahitidf, darwindf)
    ts_soi.columns = ['soi', 'soi3m']

    nino_clim, nino, ninos = load_nino()
    data = ts_soi[['soi3m']]
    index['nino5m'] = index['Nino 3.4'].rolling(window =5).mean()
    data['nino5m'] = nino.loc[:, 'anoms5m'].copy()
    dates, data = create_CEI(index[['nino5m','soi3m']], clim_start, clim_end)
    data = create_categories(data)
    data['Year'] = data.index.year
    data['Month'] = data.index.month
    data = data[['Year', 'Month', 'soi3m', 'nino5m', 'CEI', 'category', 'code']]
    datas = data  # .loc['2018':,:]

    return data, datas

