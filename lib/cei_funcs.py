import sys
sys.path.append(r'/nesi/project/niwa00004/rampaln/CAOA2101/cpp-indices/lib')
from soi_funcs import *
from figure_styles import *
from iod_funcs import *
from data_processing_funcs import *


def create_CEI(data, clim_start, clim_end):
    def zscore(x, clim_start, clim_end):
        return (x - x.loc[str(clim_start):str(clim_end)].mean()) / x.loc[str(clim_start):str(clim_end)].std()
    data = data.apply(lambda a:zscore(a, clim_start, clim_end))
    dates = data.index.to_pydatetime()
    dates = [d.toordinal() for d in dates]
    data.loc[:,'CEI'] = (data.loc[:,'soi3m'].values * -1) + data.loc[:,'nino5m'].values
    data['category'] = 'Neutral'
    data.loc[pd.isnull(data.CEI).values.flatten(),'category'] = np.nan
    data.dropna(inplace=True)
    return dates, data


def create_categories(data):

    """
    Function creates the categories based on a variety of theresholds for the CEI
    :param data:
    :return:
    """
    data.columns = ['soi3m', 'nino5m', 'CEI', 'category']
    data.loc[((data.soi3m >= +1) & (data.nino5m <= -0.5)),'category'] = 'CEI NINA'
    data.loc[((data.soi3m >= +1) & (data.nino5m < 0.5) & ( data.nino5m > -0.5)), 'category'] = 'SOI NINA'
    data.loc[((data.nino5m <= -0.5) & (data.soi3m > -1) & ( data.soi3m < 1)), 'category'] = 'NINO3.4 NINA'
    data.loc[((data.nino5m >= 0.5) & (data.soi3m < 1) & ( data.soi3m > -1)), 'category'] = 'NINO3.4 NINO'
    data.loc[((data.soi3m <= -1) & (data.nino5m < 0.5) & ( data.nino5m > -0.5)), 'category'] = 'SOI NINO'
    data.loc[((data.soi3m <= -1) & (data.nino5m >= 0.5)), 'category'] = 'CEI NINO'
    data['code'] = 0
    data.loc[pd.isnull(data.CEI),'code'] = np.nan
    data.loc[((data.soi3m >= +1) & (data.nino5m <= -0.5)),'code'] = -3
    data.loc[((data.soi3m >= +1) & (data.nino5m < 0.5) & ( data.nino5m > -0.5)), 'code'] = -2
    data.loc[((data.nino5m <= -0.5) & (data.soi3m > -1) & ( data.soi3m < 1)), 'code'] = -1
    data.loc[((data.nino5m >= 0.5) & (data.soi3m < 1) & ( data.soi3m > -1)), 'code'] = 1
    data.loc[((data.soi3m <= -1) & (data.nino5m < 0.5) & ( data.nino5m > -0.5)), 'code'] = 2
    data.loc[((data.soi3m <= -1) & (data.nino5m >= 0.5)), 'code'] = 3
    return data


def add_categories(ax, data):
    ax.plot(data.index, data.CEI, 'k-', lw=2)

    ax.plot(data.index[data['category'] == 'CEI NINA'], data.CEI[data['category'] == 'CEI NINA'], 'b*', markersize=15, label='CEI NINA')
    ax.plot(data.index[data['category'] == 'CEI NINO'], data.CEI[data['category'] == 'CEI NINO'], 'r*',  markersize=15, label = 'CEI NINO')

    ax.plot(data.index[data['category'] == 'SOI NINA'], data.CEI[data['category'] == 'SOI NINA'], 'bo', label='SOI NINA')
    ax.plot(data.index[data['category'] == 'SOI NINO'], data.CEI[data['category'] == 'SOI NINO'], 'ro', label='SOI NINO')

    ax.plot(data.index[data['category'] == 'NINO3.4 NINA'], data.CEI[data['category'] == 'NINO3.4 NINA'], 'bv', markersize=15, label='NINO3.4 NINA')
    ax.plot(data.index[data['category'] == 'NINO3.4 NINO'], data.CEI[data['category'] == 'NINO3.4 NINO'], 'rv', markersize=15, label='NINO3.4 NINO')

    ax.axhline(0, color='k', ls=':')

    ax.legend(loc='upper right')

    ax.grid(color='w')

    bounds = ax.get_xlim()

    ax.set_xlim((bounds[0] - 60, bounds[1] + 60))

    ax.set_ylim(-5, 5);
    return ax, data


def save_data(data, parent_folder_name='CEI'):
    """

    :param data:
    :param parent_folder_name: the name where the parent folder data is contained
    :return:
    """
    output_dirs = f"./{parent_folder_name}"
    if not os.path.exists(f"./{parent_folder_name}/data"):
        os.makedirs(f"./{parent_folder_name}/data")
    data.to_csv(f"./{parent_folder_name}/data/CEI.csv")