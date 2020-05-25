import matplotlib
matplotlib.use('AGG')
from analyze import all_pcaps

from pylab import rcParams
import pandas as pd
import feather
import os
import numpy as np
from os import path
from glob import glob
from datetime import timedelta
import pdb
import matplotlib.pyplot as plt

import seaborn as sns

rcParams['figure.figsize'] = 10, 8

DATA_DIR = './data/2020-05-09/'

def load_timeslices_dataframe():
    feather_file = f"{DATA_DIR}/timeslices.feather" 

    if (path.isfile(feather_file)):
        df = pd.read_feather(feather_file).dropna()
        df = df.set_index('time')
        df['time'] = df.index
        return df
    else:
        frames = []
        for local, remote, dir in all_pcaps(data_dir=DATA_DIR):
            if remote == None:
                continue

            local_feather_file = dir + "/timeslice.feather"
            print(feather_file)
            df = pd.read_feather(local_feather_file)
            frames.append(df)

        frame = pd.concat(frames)
        frame.reset_index().to_feather(feather_file)
        df = df.set_index('time')
        df['time'] = df.index
        return frame


def plot_average_downloads(df):
    plt.close()
    for protocol, data in df.groupby('protocol'):
        means = []
        for size, d in data.reset_index(drop=True).groupby('file_size'):
            d = d.mean()
            d['file_size'] = size
            means.append(d)
        
        means = pd.DataFrame(means)

        plt.scatter(means['file_size'] / 1e6, pd.to_timedelta(means['time'], unit='ns').astype('timedelta64[s]'), label=protocol, alpha=0.5)

    plt.xscale('linear')
    plt.yscale('linear')
    plt.xlabel('megabytes downloaded')
    plt.ylabel('seconds')
    plt.legend()
    plt.savefig(f"{DATA_DIR}/time_download.png")
    plt.close()

def sbrn(df):
    """
    seaborn scatter plot with estimators for each file size
    """
    plt.close()
    df = df.copy()
    df['file_size'] /= 1e6
    df['time'] = pd.to_timedelta(df['time'], unit='ns').astype('timedelta64[s]')
    
    for protocol, data in df.groupby('protocol'):
        sns.regplot(x='file_size', y='time', data=data, x_estimator=np.mean, label=protocol, scatter_kws={'s': 2})

    plt.xlabel('megabytes downloaded')
    plt.ylabel('seconds')
    plt.legend()
    plt.savefig(f"{DATA_DIR}/time_download.png")
    plt.close()

def cdf_downloads(df, column='time'):
    plt.close()

    for protocol, data in df.groupby('protocol'):
        sorted = data[column].sort_values().reset_index(drop=True)
        plt.plot(sorted, sorted.index * 100 /
                sorted.count(), label=protocol)

    plt.legend()
    plt.ylabel("Percent")
    plt.xlabel(f"{column} to download")
    plt.title(f"CDF of {column} to download filesize")
    plt.savefig(f"{DATA_DIR}/cdf_{column}.png")


def main():
    df = load_timeslices_dataframe()
    cdf_downloads(df)
    sbrn(df)

if __name__ == "__main__":
    main()