import matplotlib as mpl
mpl.use('AGG')
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

mpl.style.use('seaborn-paper')
rcParams['figure.figsize'] = 10,8
# rcParams['savefig.pad_inches'] = 0.5
rcParams['figure.constrained_layout.use'] = True
mpl.rcParams['font.size'] =  15.0

import matplotlib.pylab as pylab
params = {'legend.fontsize': 'x-large',
         'axes.labelsize': 'x-large',
         'axes.titlesize':'x-large',
         'xtick.labelsize':'x-large',
         'ytick.labelsize':'x-large'}
pylab.rcParams.update(params)


labelmap = {
    'pcc': 'PCC',
    'bbr': 'BBR',
    'cubic': 'Cubic',
    'hybla' : 'Hybla'
}

colormap = {
    'pcc': 'firebrick',
    'bbr': 'olivedrab',
    'cubic': 'teal',
    'hybla' : 'darkorchid'
}

DATA_DIR = './data/2020-07-21/'

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
            try:
                df = pd.read_feather(local_feather_file)
            except:
                continue
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

        plt.scatter(means['file_size'] / 1e6, pd.to_timedelta(means['time'], unit='ns').astype('timedelta64[s]'), label=labelmap[protocol], color=colormap[protocol], alpha=0.5)

    plt.xscale('linear')
    plt.yscale('linear')
    plt.xlabel('Download Size (Mb)')
    plt.ylabel('Time (s)')
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
        sns.regplot(x='file_size', y='time', data=data, x_estimator=np.mean, label=labelmap[protocol], color=colormap[protocol], scatter_kws={'s': 2})

    plt.xlabel('Download Size (Mb)')
    plt.ylabel('Time (s)')
    plt.legend()
    plt.savefig(f"{DATA_DIR}/time_download.png")
    plt.close()

def cdf_downloads(df, column='time'):
    plt.close()

    for protocol, data in df.groupby('protocol'):
        sorted = data[column].sort_values().reset_index(drop=True)
        plt.plot(sorted, sorted.index * 100 /
                sorted.count(), label=labelmap[protocol], color=colormap[protocol])

    plt.legend()
    plt.ylabel("Percent")
    plt.xlabel(f"{column} to download")
    plt.savefig(f"{DATA_DIR}/cdf_{column}.png")


def main():
    df = load_timeslices_dataframe()
    cdf_downloads(df)
    sbrn(df)

if __name__ == "__main__":
    main()