# plot single flow (given by directory)
# 
import matplotlib as mpl
mpl.use('AGG')
from matplotlib.pyplot import ylim
import matplotlib.pyplot as plt
import pdb
from command import run
from datetime import timedelta
from glob import glob
from os import path
import numpy as np
import os
import feather
import pandas as pd

mpl.style.use('seaborn')
font = {'family': 'Dejavu Sans',
        'size': 24}

mpl.rcParams['figure.figsize'] = 10, 8
mpl.rcParams.update({'font.size': 24})

number = "frame.number"
time_epoch = "frame.time_epoch"
src = "eth.src"
dst = "eth.dst"
src = "ip.src"
dst = "ip.dst"
srcport = "tcp.srcport"
dstport = "tcp.dstport"
seq = "tcp.seq"
ack_rtt = "tcp.analysis.ack_rtt"
proto = "ip.proto"
time = "frame.time"

def scratch():
    pass

def load_dataframe(filename, reparse=False) -> pd.DataFrame:
    """
    opens csvfile and writes out .feather file

    return: dataframe
    """
    base, _ext = path.splitext(filename)
    feather_file = base + '.feather'
    if (path.isfile(feather_file) and not reparse):
        return feather.read_dataframe(feather_file)
    else:
        print(f"regenerating feather file for {filename}")
        df = pd.read_csv(filename)
        df['time'] = pd.to_datetime(
            df['frame.time'], infer_datetime_format=True)
        feather.write_dataframe(df, feather_file)
        return df

def window_by_second(df):
    df['second'] = df.time.dt.minute * 60 + df.time.dt.second
    max_seqs = df[seq].cummax()
    df['retransmission'] = (df[seq] < max_seqs).astype(int)
    df['retransmission_count'] = df['retransmission'].cumsum()
    seconds = df[df.second > df.second.min() + 1][df.second < df.second.max() - 1] .groupby('second')
    tput = (seconds[seq].max() - seconds[seq].min()) / 125000
    clocktime = seconds.time.min()

    num_packets = seconds[seq].count()
    retransmitted_count = seconds['retransmission_count'].max() - seconds['retransmission_count'].min()
    loss = (retransmitted_count / num_packets) * 100

    return pd.DataFrame({ 'second': tput.index, 'throughput': tput, time: clocktime, 'loss': loss })

def stacked_plot(directory, machine, output_file='temp.png'):
    plt.close()
    local_fname = f"{directory}/local_sender.csv"
    remote_fname = f"{directory}/{machine}_sender.csv"
    df = load_dataframe(local_fname)
    _rdf = load_dataframe(remote_fname)

    brdf = load_dataframe(f"{directory}/{machine}.csv")
    brdf = brdf[brdf[ack_rtt] > .3]

    fig, axes = plt.subplots(nrows=3, ncols=1, sharex=True)
    tput, rtt, loss = axes
    mbps = window_by_second(df)

    df['relative_time'] = (df.time - df.time.min()).dt.total_seconds()
    brdf['relative_time'] = (brdf.time - brdf.time.min()).dt.total_seconds()
    mbps['relative_time'] = (mbps[time] - mbps[time].min()).dt.total_seconds()

    # sequence.plot(df.relative_time, df[seq])
    # sequence.set_ylabel('sequence')
    # sequence.set_ylim(ymin=0)
    # sequence.yaxis.set_major_locator(plt.MaxNLocator(4))

    tput.plot(mbps['relative_time'], mbps['throughput'])
    tput.set_ylabel('Tpu (Mb/s)')
    tput.set_ylim(ymin=0, ymax=300)
    tput.yaxis.set_major_locator(plt.MaxNLocator(4))

    rtt.plot(brdf.relative_time, brdf[ack_rtt] * 1000)
    rtt.set_ylabel('RTT (ms)')
    rtt.set_ylim(ymin=0, ymax=5000)
    rtt.yaxis.set_major_locator(plt.MaxNLocator(4))

    loss.plot(mbps['relative_time'], mbps['loss'])
    loss.set_ylabel('retransmission\nrate')
    loss.set_ylim(ymin=0, ymax=100)
    loss.yaxis.set_major_locator(plt.MaxNLocator(4))

    fig.savefig(output_file)






MACHINE = 'mlc1'
PROTOCOL = 'cubic'
TRIAL = '0'
DIR = f'./data/2020-06-01/{MACHINE}_{PROTOCOL}_{TRIAL}'
def main():
    day = './data/2020-07-21/'
    data = []
    for trial in [1, 2, 3, 4, 5]:
    # for trial in [1]:
        data += [('mlcnetA.cs.wpi.edu', 'cubic', str(trial)), ('mlcnetB.cs.wpi.edu', 'bbr', str(trial)), ('mlcnetC.cs.wpi.edu', 'hybla', str(trial))]

    for machine, protocol, trial in data:
        dir = f"{day}/{machine}_{protocol}_{trial}"
        print(dir)
        stacked_plot(dir, machine, output_file=f"{day}/stacked_{protocol}_{trial}.png")

if __name__ == "__main__":
    main()