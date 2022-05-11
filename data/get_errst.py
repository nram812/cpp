import sys
from datetime import datetime
import pathlib
import datetime
import os
import ftplib
import ftplib
from multiprocessing import Pool
import json
# load json file with config
with open('data_config.json', 'r') as f:
    config = json.load(f)
download_loc = config['ersst']


class DownloadData:

    def __init__(self, base_url = 'ftp.ncdc.noaa.gov',
                 download_loc = download_loc):
        """

        :param base_url: base_url to retrieve data, please do not change
        :param download_loc: the location where to download the data to.
        """
        self.base_url = base_url
        self.local_path = download_loc
        # make directory if it doesn't exist
        if not os.path.exists(self.local_path):
            os.mkdir(self.local_path)

        self.local_files = [file for file in os.listdir(self.local_path)
                            if ("ersst" in file)
                            & (".nc" in file)]
        self.remote_names = self.get_url_paths()
        # find the files that are missing from the list
        missing_files = []
        for idx, file in enumerate(self.remote_names):
            if file not in self.local_files:
                if file.endswith(".nc"):
                    missing_files.append(self.remote_names[idx])
        self.missing_files = missing_files

    def get_url_paths(self):
        """
        Connects to the ftp database and retieves files
        :return:
        """
        ftp = ftplib.FTP('ftp.ncdc.noaa.gov', 'anonymous')
        ftp.cwd("pub/data/cmb/ersst/v5/netcdf/")
        files = ftp.nlst()
        remote_files = files
        date_avail = remote_files[-1].split('.')[-2]
        last_avail = datetime.datetime.strptime(date_avail+'01', "%Y%m%d")
        lag = (datetime.datetime.utcnow() - last_avail).days
        if lag >= 70:
            print(r"Warning, the last available date on the NOAA server "
                  r"({last_avail:%Y-%m}) is more than 70 days old ({lag} days ...)")

        return remote_files

    def download_file(self, filename):
        path = self.local_path
        try:
            ftp = ftplib.FTP('ftp.ncdc.noaa.gov', 'anonymous')
            ftp.cwd("pub/data/cmb/ersst/v5/netcdf/")
            handle = open(path.rstrip("/") + "/" + filename.lstrip("/"), 'wb')
            ftp.retrbinary('RETR %s' % filename, handle.write)

        except:
            print("download failed")


def download_data(dataset,
                  download_function,
                  agents = 1, chunksize =1):
    """

    :param download_function:
    :param agents:
    :param chunksize:
    :param dataset: list of files to download from ftp database
    :return:
    """
    if len(dataset) > 0.0:
        arr = []
        for dset in dataset:
            download_function(dset)


if __name__ == '__main__':
    cls = DownloadData(download_loc=download_loc)
    dataset = cls.missing_files
    download_data(dataset, download_function=cls.download_file)

