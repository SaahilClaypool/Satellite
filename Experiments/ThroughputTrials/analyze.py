# from analyze import *
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt

from command import run
from datetime import timedelta
from glob import glob
from os import path
import numpy as np
import os
import feather
import pandas as pd


from pylab import rcParams
rcParams['figure.figsize'] = 10, 8



DATA_DIR = './data/2020-05-09/'

LOCAL = '192.168.1.102'
RECEIVER = LOCAL


def all_pcaps(data_dir=DATA_DIR):
    for dir in glob(f"{data_dir}/*"):
        if (not path.isdir(dir)):
            continue

        local = glob(f"{dir}/local.pcap")
        remote = [f for f in filter(lambda fname: not "local" in fname,
                                    glob(f"{dir}/*"))]
        remote = remote[0] if remote else None
        local = local[0] if local else None

        yield((local, remote, dir))

def pcap_to_csv(pcap_file='./data/pcap.pcap', reparse=True):
    """
    TODO this is optional
    """
    output_file = path.splitext(pcap_file)[0] + '.csv'

    command = f"""
    tshark -r {pcap_file} \
        -T fields  \
        -e frame.number  \
        -e frame.time_epoch  \
        -e eth.src  \
        -e eth.dst  \
        -e ip.src  \
        -e ip.dst  \
        -e tcp.srcport \
        -e tcp.dstport \
        -e tcp.seq \
        -e tcp.analysis.ack_rtt \
        -e ip.proto  \
        -e frame.time \
        -E header=y  \
        -E separator=,  \
        -E quote=d  \
        -E occurrence=f \
        > {output_file}
        """
    if reparse or not path.exists(output_file):
        run(command).wait()
    return output_file


def select_data_flow(groups):
    max_packets = 0
    max_group = pd.DataFrame()
    for _name, group in groups:
        group = group.reset_index()
        packets = len(group.index)
        if packets > max_packets:
            max_packets = packets
            max_group = group
    return max_group

def update_dataframe(df, filename):
    base, _ext = path.splitext(filename)
    feather_file = base + '.feather'
    feather.write_dataframe(df, feather_file)
    return df

def load_dataframe(filename):
    """
    opens csvfile and writes out .feather file

    return: dataframe
    """
    base, _ext = path.splitext(filename)
    feather_file = base + '.feather'
    if (path.isfile(feather_file)):
        return feather.read_dataframe(feather_file)
    else:
        df = pd.read_csv(filename)
        df['time'] = pd.to_datetime(df['frame.time'], infer_datetime_format=True)
        feather.write_dataframe(df, feather_file)
        return df

def parsed_filenames(filename):
    base, _ext = path.splitext(filename)
    receiver_path = base + '_receiver.feather'
    sender_path = base + '_sender.feather'
    return sender_path, receiver_path

def parse_csv(filename):
    """
    return pandas version of the csv
    """
    sender_path, receiver_path = parsed_filenames(filename)

    if (path.isfile(receiver_path) and path.isfile(sender_path)):
        receiver_flow = feather.read_dataframe(receiver_path)
        sender_flow = feather.read_dataframe(sender_path)
        return (sender_flow, receiver_flow)


    df = load_dataframe(filename).dropna()
    df = df.set_index('frame.time').sort_index()

    group_tuple = ["ip.src", "ip.dst", "tcp.srcport", "tcp.dstport"]

    sender_traffic = df[df['ip.src'] != LOCAL].groupby(group_tuple)
    sender_flow = select_data_flow(sender_traffic)
    feather.write_dataframe(sender_flow, sender_path)

    receiver = df[df['ip.src'] == RECEIVER].groupby(group_tuple)
    receiver_flow = select_data_flow(receiver)
    feather.write_dataframe(receiver_flow, receiver_path)

    return (sender_flow, receiver_flow)

def parse_directory(directory):
    """
    expect directory like "data/2020-05-02/mlc1_cubic_54"
    """
    base = os.path.basename(directory)
    parts = base.split('_')
    host = parts[0]
    protocol = 'cubic'
    if len(parts) > 2:
        protocol = parts[1]
    return host, protocol


def summary(df, directory=None):

    host, protocol = parse_directory(directory)

    if df.empty:
        return {}, 0, 0, 0

    start_time = df['frame.time'][0]

    total = lambda key: df[key].max() - df[key].min()

    total_time = total('time')
    total_bytes = total('tcp.seq')
    throughput_mbps = (total_bytes / total_time.seconds) / 125000

    df['second'] = df.time.dt.minute * 60 + df.time.dt.second
    seconds = df[df.second > (df.second.min() + 10)] .groupby('second')
    mbps = (seconds['tcp.seq'].max() - seconds['tcp.seq'].min()) / 125000

    quantile_cutoffs = [
        0,
        .1,
        0.25,
        0.5,
        0.75, 
        0.9,
        1.0
    ]

    quantiles = dict([(str(q), mbps.quantile(q)) for q in quantile_cutoffs])
    quantiles["mean"] = throughput_mbps


    if directory:
        summary = f"""\
        ----------------------
        total time: {total_time}
        total bytes: {total_bytes}
        tp (mbps): {throughput_mbps}
        quantiles: {quantiles}
        ----------------------
        """
        with open(f"{directory}/summary.txt", 'a') as outfile:
            outfile.write(summary)

    return quantiles, host, protocol, start_time


def analyze(local, remote, dir):
    print(local, remote)
    local_csv = pcap_to_csv(local, False)
    local_sender_flow, local_receiver_flow = parse_csv(local_csv)
    # remote_sender_flow, remote_receiver_flow = parse_csv(local_csv)
    return [summary(local_sender_flow, dir),
            # summary(local_receiver_flow, dir),
            None,
            # summary(remote_sender_flow, dir), 
            None, 
            # summary(remote_receiver_flow, dir)]
            None]


def main():
    throughputs = []
    for local, remote, dir in all_pcaps():
        quantiles, host, protocol, start_time = analyze(local, remote, dir)[0]
        quantiles['host'] = host
        quantiles['protocol'] = protocol
        quantiles['start_time'] = start_time
        throughputs.append(quantiles)

    df = pd.DataFrame(throughputs)
    df.to_csv(f"{DATA_DIR}/quantiles.csv")


def timeslice(filename):
    """
    determine the time it takes to 
    """
    dirname = path.dirname(filename)
    sender_path, receiver_path = parsed_filenames(filename)
    sender = feather.read_dataframe(sender_path)
    gig = 1e+9
    num_objects = 100
    times = []
    base_time = sender.time.min()

    for i in range(num_objects):
        bytes_to_download = (i + 1) * (gig / num_objects)
        time_to_download = sender[sender['tcp.seq'] > bytes_to_download].iloc[0].time - base_time
        times.append({ 'file_size': bytes_to_download, 'time': time_to_download })

    df = pd.DataFrame(times)
    df.to_feather(dirname + '/timeslice.feather')

    plt.close()
    plt.plot(df.file_size / gig, df.time * 1e-9)
    plt.xlabel('Download gig')
    plt.ylabel('Time (seconds)')
    plt.savefig(dirname + '/slice.png')

    print(times)

def retrofit_times(directory):
    """
    doesn't give good data...
    """
    directory = './data/2020-05-05/'
    start_times = []
    dirs = [dir for (_, _, dir) in all_pcaps()]
    csvfile = f'{directory}/quantiles.csv'
    quantiles_df = load_dataframe(csvfile)
    for d in dirs:
        data_df = pd.read_csv(f'{d}/local.csv', nrows=2)
        start_time = data_df['frame.time'][0]
        start_times.append(start_time)

    quantiles_df['start_time'] = start_times
    quantiles_df.to_csv(csvfile)

if __name__ == "__main__":
    main()
