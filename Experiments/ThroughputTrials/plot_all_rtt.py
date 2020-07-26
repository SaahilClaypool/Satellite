import math as m
from pylab import rcParams
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from analyze import *
import matplotlib
matplotlib.use('AGG')


plt.style.use('seaborn')
rcParams['figure.figsize'] = 10, 8
# plot_rtt_cdf(all_rtts)


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
time = "time"
proto = "protocol"


def resample(df, window='1s'):
    df = df.set_index(time).sort_index()
    r = df.resample(window)
    return r


def single_dataframe_rtt(second_half = False):
    all_dataframes = []
    for _local, remote, dir in [i for i in all_pcaps()]:
        try:
            _, remote_receiver = parsed_filenames(remote)
            _, protocol = parse_directory(dir)
            df = load_dataframe(remote_receiver)[[time, ack_rtt]].dropna()
            if second_half:
                df = df.tail(int(df.shape[0] / 2))
            resampled = resample(df)
            df = resampled.mean()

            df['protocol'] = protocol
            all_dataframes.append(df)
        except:
            next
    return pd.concat(all_dataframes)


def single_dataframe_retransmission(second_half = False):
    all_dataframes = []
    for local, _remote, dir in [i for i in all_pcaps()]:
        try:
            local_sender, _ = parsed_filenames(local)
            df = load_dataframe(local_sender)[[time, seq]].dropna()
            if second_half:
                df = df.tail(int(df.shape[0] / 2))
            _, protocol = parse_directory(dir)

            max_seqs = df[seq].cummax()
            df['retransmission'] = (df[seq] < max_seqs).astype(float)
            resampled = resample(df)

            retrans_rate = resampled['retransmission'].sum(
            ) / resampled['retransmission'].count()
            df = resampled.mean()
            df['retransmission'] = retrans_rate

            df['protocol'] = protocol
            all_dataframes.append(df)
        except Exception as e:
            next
    return pd.concat(all_dataframes)


def plot_rtt_cdf(df, prefix=""):
    plt.close()

    for protocol, data in df.groupby('protocol'):
        sorted_rtt = data[ack_rtt].sort_values().reset_index()
        plt.plot(sorted_rtt[ack_rtt], sorted_rtt.index /
                 sorted_rtt[ack_rtt].count() * 100, label=protocol)

    plt.legend()
    plt.ylabel("Percent")
    plt.xlabel(f"Ack rtt (seconds)")
    plt.savefig(f"{DATA_DIR}/{prefix}ack_rtt.png")


def plot_retransmission_cdf(df, prefix=""):
    plt.close()

    for protocol, data in df.groupby('protocol'):
        sorted_rtt = data['retransmission'].sort_values().reset_index()
        plt.plot(sorted_rtt['retransmission'] * 100, sorted_rtt.index /
                 sorted_rtt['retransmission'].count() * 100, label=protocol)

    plt.legend()
    plt.ylabel("Percent")
    plt.xlabel(f"Retransmission Rate (%)")
    plt.savefig(f"{DATA_DIR}/{prefix}retrans.png")

def plot_all():
    all_rtts = single_dataframe_rtt()
    plot_rtt_cdf(all_rtts)

    all_retransmission = single_dataframe_retransmission()
    plot_retransmission_cdf(all_retransmission)

    all_rtts = single_dataframe_rtt(second_half=True)
    plot_rtt_cdf(all_rtts, prefix="steady_")

    all_retransmission = single_dataframe_retransmission(second_half=True)
    plot_retransmission_cdf(all_retransmission, prefix="steady_")


if __name__ == "__main__":
    plot_all()
