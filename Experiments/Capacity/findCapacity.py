#!/usr/bin/python3
"""
Before starting - make sure iperf is working on the remote machine

Will do the following:

1. Start tcpdump in the background listening on the correct port
2. Setup the parameters we are looking for
3. 
"""

from subprocess import Popen

def run_iperf(host="mlc1.cs.wpi.edu", seconds=300, port=5201):
  command = f"iperf3 -c {host} -t {seconds} -R"
  proc = Popen(command, shell=True)
  return proc

def run_tcpdump(filename='./data/pcap.pcap', port=5201):
  command = f"tcpdump -i eno2 -s 96 port 5201 -w {filename}"
  proc = Popen(command, shell=True)
  return proc

def run_tshark(pcap_file='./data/pcap.pcap', outout_file='./data/csv.csv'):
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
    -e ip.proto  \
    -E header=y  \
    -E separator=,  \
    -E quote=d  \
    -E occurrence=f
    """
  print(command)
  proc = Popen(command, shell=True)
  return proc


def main():
  tcpdump = run_tcpdump()
  iperf = run_iperf(seconds=300)
  print('started iperf')
  iperf.wait()
  print('iperf done')
  tcpdump.kill()
  print('wrote pcap')


if __name__ == "__main__":
  main()