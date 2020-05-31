#!/usr/bin/python3
"""
plot a single pcap with tcp trace
"""

from command import run
import os

def main():
    graph_data()

def graph_data(pcap="./data/2020-05-09/mlc2_bbr_10/mlc2.pcap", output_dir="tcptrace_graphs/"):
  run(f"tcptrace -N -R -T  --output_dir={output_dir} {pcap}").wait()
  cur_dir = os.getcwd()
  os.chdir(output_dir)
  for f in os.listdir():
    filename, extension = os.path.splitext(f)
    if extension == ".xpl":
      run(f"xpl2gpl {f}").wait()
      run(f"gnuplot -e \"set terminal png size 1200,900; set output '{filename}.png'\" {filename}.gpl").wait()
  os.chdir(cur_dir)

if __name__ == "__main__":
    main()