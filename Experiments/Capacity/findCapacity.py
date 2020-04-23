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

def run_tcpdump(filename='./data/pcap.pcap', port=5201, device="eno2", user="", host=""):
  """
  mlc1 uses ens3
  """
  command = f"sudo tcpdump -Z $USER -i {device} -s 96 port 5201 -w {filename}" # will drop permissions with -Z
  return run_command(command, user, host)

def kill_tcpdump(user="", host=""):
  command = f"pkill tcpdump"
  return run_command(command, user, host)


def copy_pcap(filename="./data/pcap", output_folder="./data", user="", host=""):
  cp = "cp"
  if (len(user) > 0):
    user+="@"
  if (len(host) > 0):
    cp = "scp"
    host += ":"

  command = f"{cp} {user}{host}{filename} {output_folder}"
  global MOCK
  if MOCK:
    print(f"would run: {command}")
  else:
    Popen(command, shell=True).wait()


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


def tune_tc(algorithm="cubic", tcp_mem_size=8388608, host="mlc1.cs.wpi.edu", user=""):
  tcp_mem_size = int(tcp_mem_size)
  command = f"\
sudo sysctl -w net.ipv4.tcp_mem='{tcp_mem_size} {tcp_mem_size} {tcp_mem_size}' && \
sudo sysctl -w net.ipv4.tcp_wmem='{tcp_mem_size} {tcp_mem_size} {tcp_mem_size}' && \
sudo sysctl -w net.ipv4.tcp_rmem='{tcp_mem_size} {tcp_mem_size} {tcp_mem_size}' && \
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

def run_wmem_test(mem=8388608):
  graph_dir = f'./graphs/wmem_{mem}/'
  if not os.path.exists(graph_dir):
    os.mkdir(graph_dir)

  pcap_file = f'./data/pcap_{mem}.pcap'

  tune_tc(host="mlc1.cs.wpi.edu", tcp_mem_size=mem, algorithm="bbr")
  tune_tc(host="", tcp_mem_size=mem, algorithm="bbr")

  tcpdump = run_tcpdump(filename=pcap_file)
  mlc1_tcpdump = run_tcpdump(filename=pcap_file, device="ens3", host="mlc1")
  sleep(10)

  iperf = run_iperf(seconds=300)
  print('started iperf')
  iperf.wait()
  print('iperf Done')

  tcpdump.send_signal(2)
  mlc1_tcpdump.send_signal(2)
  mlc1_tcpdump.send_signal(2)
  kill_tcpdump(host="mlc1")
  print("waiting for tcpdump to finish on remote")
  mlc1_tcpdump.wait()
  sleep(10)
  print('wrote pcap')

  copy_pcap(pcap_file, host="mlc1", output_folder='./data/mlc1/')
  # graph_data(pcap_file, graph_dir)
  

def main():
  global MOCK
  MOCK = False

  tput = 75 # megabits per second
  byetes_per_megabit = 125000
  rtt = 700.00 / 100 # seconds
  bdp = int(tput * byetes_per_megabit * rtt) # bytes

  # run_tshark().wait()
  run_wmem_test(mem=bdp)
  # run_wmem_test(mem=int(0.5 * bdp)) 
  # run_wmem_test(mem=2 * bdp)
  # run_wmem_test(mem=int(0.25 * bdp)) 
  # run_wmem_test(mem=4 * bdp)


if __name__ == "__main__":
  main()
