import matplotlib as mpl
mpl.use('AGG')
font = { 'size'   : 40 }
from pylab import rcParams
rcParams['figure.figsize'] = 10, 8
import pdb
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math as m


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

# DATA_DIR = './data/2020-05-09/'
# DATA_DIR = './data/2020-06-01/'
# DATA_DIR = './data/2020-07-12/'
DATA_DIR = './data/2020-07-27/'

global PREFIX
PREFIX = ""


def plot_rtt_cdf(df, column='mean'):
    plt.close()

    for protocol, data in df.groupby('protocol'):
        sorted_rtt = data[column].sort_values().reset_index()
        plt.plot(sorted_rtt[column], sorted_rtt.index /
                 sorted_rtt[column].count() * 100, label=labelmap[protocol], color=colormap[protocol])

    plt.legend()
    plt.ylabel("Cumulative Distribution\n(percent)")
    plt.xlabel(f"RTT (ms)")
    plt.savefig(f"{DATA_DIR}/{PREFIX}cdf_rtt_{column}.png")

def plot_loss_cdf(df):
    column = 'loss'
    plt.close()

    print(df.head())
    for protocol, data in df.groupby('protocol'):
        data = data[data['loss'] < 0.95]
        sorted_loss = data[column].sort_values().reset_index()
        plt.plot(sorted_loss[column] * 100, sorted_loss.index /
                 sorted_loss[column].count() * 100, label=labelmap[protocol], color=colormap[protocol])

    plt.legend()
    plt.ylabel("Cumulative Distribution\n(percent)")
    plt.xlabel(f"Retranmission\n(percent)")
    plt.savefig(f"{DATA_DIR}/{PREFIX}cdf_{column}.png")




def plot_througput_cdf(df, column='mean'):
    plt.close()

    for protocol, data in df.groupby('protocol'):
        sorted_throughput = data[column].sort_values().reset_index()
        plt.plot(sorted_throughput[column], sorted_throughput.index /
                 sorted_throughput[column].count() * 100, label=labelmap[protocol], color=colormap[protocol])

    plt.legend()
    plt.ylabel("Percent")
    plt.xlabel(f"{column} throughput")
    plt.savefig(f"{DATA_DIR}/{PREFIX}cdf_{column}.png")

def summary_statistics(prefix=PREFIX):
    global PREFIX
    fname = f"{DATA_DIR}/{prefix}quantiles.csv"
    print(f"summary of {fname}")
    df = pd.read_csv(fname, index_col=0).dropna(how='all')
    mean = df.groupby('protocol').mean()['mean']
    std = df.groupby('protocol').std()['mean']
    print(f'{prefix} mean throughput', mean)
    print(f'{prefix} std throughput', std)
    with open('out.txt', 'w') as output_file:
        print(df.groupby('protocol').describe(), file=output_file)


    fname = f"{DATA_DIR}/{prefix}rtt_quantiles.csv"
    df = pd.read_csv(fname, index_col=0).dropna(how='all')
    mean = df.groupby('protocol').mean()['mean']
    std = df.groupby('protocol').std()['mean']
    print(f'{prefix} mean rtt', mean)
    print(f'{prefix} std rtt', std)




def throughput_summary(prefix=PREFIX):
    global PREFIX

    PREFIX = prefix

    fname = f"{DATA_DIR}/{PREFIX}quantiles.csv"
    print(fname)
    df = pd.read_csv(fname, index_col=0).dropna(how='all')
    print(df)
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dropna()
    df = df.set_index('start_time').sort_index()
    df['start_time'] = df.index

    columns = ['0.1', '0.5', '0.75', 'mean']

    for column in columns:
        plot_througput_cdf(df, column)

    plt.close()
    if 'start_time' in df.keys():
        for protocol, data in df.groupby('protocol'):
            column = 'mean'
            column_name = 'mean'
            if m.isnan(data[column][0]):
                column = '0.5'
                column_name = 'median'

            plt.scatter(data.index, data[column], label=labelmap[protocol], color=colormap[protocol])

        ticks = [df['start_time'].quantile(i) for i in np.arange(0, 1, .1)]
        plt.xticks(ticks, rotation=15)
        plt.legend()
        plt.ylabel(column_name)
        date_formatter = mpl.dates.DateFormatter("%m/%d - %H:%M")
        ax = plt.gca()
        ax.xaxis.set_major_formatter(date_formatter)
        plt.savefig(f"{DATA_DIR}/{PREFIX}timeplot.png")
        plt.close()

    df = df[['0', '0.1', '0.25', '0.5', '0.75',
             '0.9', '1.0', 'mean', 'host', 'protocol']]

    df.boxplot()
    plt.savefig(f"{DATA_DIR}/{PREFIX}big_box.png")
    plt.close()

    df[['protocol', '0.1', '0.5', '0.9', 'mean']].boxplot(by='protocol')
    plt.ylim(0, 200)
    plt.savefig(f"{DATA_DIR}/{PREFIX}box_protocol.png")
    plt.close()

    df.boxplot(column=['mean'], by='protocol')
    plt.savefig(f"{DATA_DIR}/{PREFIX}mean_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.75'], by='protocol')
    plt.savefig(f"{DATA_DIR}/{PREFIX}75_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.5'], by='protocol')
    plt.savefig(f"{DATA_DIR}/{PREFIX}50_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.9'], by='protocol')
    plt.savefig(f"{DATA_DIR}/{PREFIX}90_box_protocol.png")
    plt.close()

    df.boxplot(column=['1.0'], by='protocol')
    plt.savefig(f"{DATA_DIR}/{PREFIX}100_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.25'], by='protocol')
    plt.savefig(f"{DATA_DIR}/{PREFIX}25_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.1'], by='protocol')
    plt.savefig(f"{DATA_DIR}/{PREFIX}01_box_protocol.png")
    plt.close()

    df.boxplot(column=['0'], by='protocol')
    plt.savefig(f"{DATA_DIR}/{PREFIX}00_box_protocol.png")
    plt.close()

    df.boxplot(by='host')
    plt.savefig(f"{DATA_DIR}/{PREFIX}box_machine.png")
    plt.close()


def rtt_summary(prefix=""):
    global PREFIX
    PREFIX = prefix

    fname = f"{DATA_DIR}/{PREFIX}rtt_quantiles.csv"
    df = pd.read_csv(fname, index_col=0).dropna(how='all')
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dropna()
    df = df.set_index('start_time').sort_index()
    df['start_time'] = df.index

    columns = ['0.1', '0.5', '0.75']

    for column in columns:
        plot_rtt_cdf(df, column)

    plt.close()

    df = df[['0', '0.1', '0.25', '0.5', '0.75',
             '0.9', '1.0', 'host', 'protocol']]

    df.boxplot()
    plt.savefig(f"{DATA_DIR}/{PREFIX}rtt_boxplot.png")
    plt.close()

def loss_summary(prefix=""):
    global PREFIX
    PREFIX = prefix

    fname = f"{DATA_DIR}/{PREFIX}losses.csv"
    df = pd.read_csv(fname, index_col=0).dropna(how='all')
    df['start_time'] = pd.to_datetime(df['start_time'], errors='coerce').dropna()
    df = df.set_index('start_time').sort_index()
    df['start_time'] = df.index

    plot_loss_cdf(df)
    plt.close()

    # pdb.set_trace()

    if 'start_time' in df.keys():
        for protocol, data in df.groupby('protocol'):
            column = 'loss'
            column_name = 'loss'

            plt.scatter(data.index, data[column] * 100, label=labelmap[protocol], color=colormap[protocol])

    ticks = [df['start_time'].quantile(i) for i in np.arange(0, 1, .1)]
    plt.xticks(ticks, rotation=15)
    plt.legend()
    plt.ylabel(column_name)
    date_formatter = mpl.dates.DateFormatter("%m/%d - %H:%M")
    ax = plt.gca()
    ax.xaxis.set_major_formatter(date_formatter)
    plt.savefig(f"{DATA_DIR}/{PREFIX}loss_timeplot.png")
    plt.close()

def main_summary():
    throughput_summary()
    rtt_summary()
    loss_summary()

    throughput_summary(prefix="steady_")
    rtt_summary(prefix="steady_")
    loss_summary(prefix="steady_")


if __name__ == "__main__":
    # main_summary()
    summary_statistics()
    summary_statistics(prefix="steady_")
    summary_statistics(prefix="startup_")
