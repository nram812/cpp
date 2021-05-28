import sys
from datetime import datetime
import pathlib
import datetime
import os
import ftplib
import ftplib
from multiprocessing import Pool
download_loc = "/scale_wlg_persistent/filesets/project/niwa00004/rampaln/CAOA2101/cpp-indices/IOD/"


class DownloadData:

    def __init__(self, base_url = 'ftp.ncdc.noaa.gov', download_loc = download_loc):
        self.base_url = base_url
        # Creating the patg
        self.local_path = os.path.join(download_loc,'data')
        if not os.path.exists(self.local_path):
            os.mkdir(self.local_path)

        self.local_files = [file for file in os.listdir(self.local_path) if ("ersst" in file) &(".nc" in file)] #list(self.local_path.glob("ersst.*.nc"))
        self.remote_names = self.get_url_paths()
        missing_files = []
        for idx, file in enumerate(self.remote_names):
            if file not in self.local_files:
                if file.endswith(".nc"):
                    missing_files.append(self.remote_names[idx])
        self.missing_files = missing_files#list(set(self.remote_f) - set(self.local_files))

    def get_url_paths(self):

        # Open ftp connection
        ftp = ftplib.FTP('ftp.ncdc.noaa.gov', 'anonymous')
        ftp.cwd("pub/data/cmb/ersst/v5/netcdf/")
        files = ftp.nlst()
        remote_files = files
        date_avail = remote_files[-1].split('.')[-2]
        last_avail = datetime.datetime.strptime(date_avail+'01', "%Y%m%d")
        lag = (datetime.datetime.utcnow() - last_avail).days
        if lag >= 70:
            print(
                r"Warning, the last available date on the NOAA server ({last_avail:%Y-%m}) is more than 70 days old ({lag} days ...)")

        return remote_files

    def download_file(self, filename):
        path = self.local_path#download_loc
        try:
            ftp = ftplib.FTP('ftp.ncdc.noaa.gov', 'anonymous')
            ftp.cwd("pub/data/cmb/ersst/v5/netcdf/")
            handle = open(path.rstrip("/") + "/" + filename.lstrip("/"), 'wb')
            ftp.retrbinary('RETR %s' % filename, handle.write)

        except:
            print("download failed")


print("downloading data")
if __name__ == '__main__':
    cls = DownloadData(download_loc=download_loc)
    dataset = cls.missing_files
    if len(dataset) > 0.0:
        print ('Dataset: ' + str(dataset))
        agents = 1
        chunksize = 1
        arr = []
        with Pool(processes=agents) as pool:
            result = pool.map(cls.download_file, dataset, chunksize)
    else:
        print("not downloading")

