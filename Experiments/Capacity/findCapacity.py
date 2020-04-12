#!/usr/bin/python3
"""
Before starting - make sure iperf is working on the remote machine

Will do the following:

1. Start tcpdump in the background listening on the correct port
2. Setup the parameters we are looking for
3. 
"""
MOCK = False

MLC1 = '130.215.28.30'
SENDER = MLC1
GLOMMA = '192.168.1.102'
RECEIVER = GLOMMA

from subprocess import Popen
import subprocess
from time import sleep
import os
import pandas as pd

def run_command(command, user="", host=""):
  """
  timeout = 0 to wait forever
  return proc handle
  """
  prefix = ""
  if (len(host)):
    prefix = f"{user}@" if len(user) > 0 else ""
    command = command.replace('"', '\\"')
    command = f'ssh {prefix}{host} "{command}"'


  global MOCK
  if(MOCK):
    print("would run:", command)
    return Popen("echo")

  print(command)
  proc = Popen(command, shell=True)
  return proc

def run_all(commands):
  procs = []
  for command in commands:
    procs.append(run_command(*command))
  
  for proc in procs:
    proc.wait()




def run_iperf(host="mlc1.cs.wpi.edu", seconds=300, port=5201):
  command = f"iperf3 -c {host} -t {seconds} -R"
  return run_command(command)

def run_tcpdump(filename='./data/pcap.pcap', port=5201, user="", host=""):
  command = f"sudo tcpdump -i eno2 -s 96 port 5201 -w {filename}"
  return run_command(command, user, host)

def run_tshark(pcap_file='./data/pcap.pcap', output_file='./data/csv.csv', user="", host=""):
  """
  TODO this is optional
  """
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
    -e ip.proto  \
    -e frame.time \
    -E header=y  \
    -E separator=,  \
    -E quote=d  \
    -E occurrence=f \
    > {output_file}
    """
  return run_command(command, user, host)

def select_data_flow(groups):
  max_packets = 0
  max_group = []
  for _name, group in groups:
    group = group.reset_index()
    packets = len(group.index)
    if packets > max_packets:
      max_packets = packets
      max_group = group
  return max_group

def parse_csv(csv_file='./data/csv.csv'):
  """
  return pandas version of the csv
  """
  df =  pd.read_csv(csv_file).dropna()

  group_tuple = ["ip.src", "ip.dst", "tcp.srcport", "tcp.dstport"] 

  sender_traffic = df[df['ip.src'] == SENDER].groupby(group_tuple)
  sender_flow = select_data_flow(sender_traffic)

  receiver = df[df['ip.src'] == RECEIVER].groupby(group_tuple)
  receiver_flow = select_data_flow(receiver)

  return (sender_flow, receiver_flow)


def tune_tc(algorithm="cubic", wmem_send_size=8388608, host="mlc1.cs.wpi.edu", user=""):
  command = f"\
sudo sysctl -w net.ipv4.tcp_mem='{wmem_send_size} {wmem_send_size} {wmem_send_size}' && \
sudo sysctl -w net.ipv4.tcp_wmem='{wmem_send_size} {wmem_send_size} {wmem_send_size}' && \
sudo sysctl -w net.ipv4.tcp_congestion_control='{algorithm}' \
"
  return run_command(command, user, host).wait()


def graph_data(pcap="./data/pcap.pcap", output_dir="graphs/"):
  run_command(f"tcptrace -N -R -T  --output_dir={output_dir} {pcap}").wait()
  cur_dir = os.getcwd()
  os.chdir(output_dir)
  for f in os.listdir():
    filename, extension = os.path.splitext(f)
    if extension == ".xpl":
      run_command(f"xpl2gpl {f}").wait()
      run_command(f"gnuplot -e \"set terminal png size 1200,900; set output '{filename}.png'\" {filename}.gpl").wait()

  for f in os.listdir():
    filename, extension = os.path.splitext(f"{f}")
    if extension != ".png":
      run_command(f"rm {f}").wait()

  os.chdir(cur_dir)

def run_wmem_test(wmem=8388608):
  graph_dir = f'./graphs/wmem_{wmem}/'
  if not os.path.exists(graph_dir):
    os.mkdir(graph_dir)

  pcap_file = f'./data/pcap_{wmem}.pcap'

  tune_tc(host="mlc1.cs.wpi.edu", wmem_send_size=wmem)

  tcpdump = run_tcpdump(filename=pcap_file)
  sleep(5)

  iperf = run_iperf(seconds=300)
  print('started iperf')
  iperf.wait()
  print('iperf Done')

  tcpdump.send_signal(2)
  sleep(1)
  print('wrote pcap')

  # graph_data(pcap_file, graph_dir)
  

def main():
  global MOCK
  MOCK = False

  # run_tshark().wait()
  run_wmem_test(wmem=int(0.5 * 360000000)) # I think this is roughly 1 bdp...
  run_wmem_test(wmem=360000000)
  run_wmem_test(wmem=2 * 360000000)
  run_wmem_test(wmem=4 * 360000000)


if __name__ == "__main__":
  main()
