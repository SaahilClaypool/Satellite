import matplotlib
matplotlib.use('AGG')

from pylab import rcParams
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


rcParams['figure.figsize'] = 10, 8

DATA_DIR = './data/2020-05-09/'


def analyze_summary():
    fname = f"{DATA_DIR}/quantiles.csv"
    df = pd.read_csv(fname, index_col=0).dropna()
    df['start_time'] = pd.to_datetime(df['start_time'])
    df = df.set_index('start_time').sort_index()
    df['start_time'] = df.index


    if 'start_time' in df.keys():
        for protocol, data in df.groupby('protocol'):
            plt.scatter(data.index, data['mean'], label=protocol)

        ticks = [df['start_time'].quantile(i) for i in np.arange(0, 1, .1)]
        plt.xticks(ticks, rotation=15)
        plt.legend()
        date_formatter = matplotlib.dates.DateFormatter("%m/%d - %H:%M")
        ax = plt.gca()
        ax.xaxis.set_major_formatter(date_formatter)
        plt.savefig(f"{DATA_DIR}/timeplot.png")
        plt.close()

    df = df[['0', '0.1', '0.25', '0.5', '0.75',
             '0.9', '1.0', 'mean', 'host', 'protocol']]

    df.boxplot()
    plt.title("Throughput by quartile")
    plt.savefig(f"{DATA_DIR}/big_box.png")
    plt.close()

    df.boxplot(by='protocol')
    plt.savefig(f"{DATA_DIR}/box_protocol.png")
    plt.close()

    df.boxplot(column=['mean'], by='protocol')
    plt.savefig(f"{DATA_DIR}/mean_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.75'], by='protocol')
    plt.savefig(f"{DATA_DIR}/75_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.5'], by='protocol')
    plt.savefig(f"{DATA_DIR}/50_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.9'], by='protocol')
    plt.savefig(f"{DATA_DIR}/90_box_protocol.png")
    plt.close()

    df.boxplot(column=['1.0'], by='protocol')
    plt.savefig(f"{DATA_DIR}/100_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.25'], by='protocol')
    plt.savefig(f"{DATA_DIR}/25_box_protocol.png")
    plt.close()

    df.boxplot(by='host')
    plt.savefig(f"{DATA_DIR}/box_machine.png")
    plt.close()


if __name__ == "__main__":
    analyze_summary()
