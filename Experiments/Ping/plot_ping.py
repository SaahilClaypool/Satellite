#!/usr/bin/python3

import matplotlib
matplotlib.use('AGG')

import pandas as pd
import matplotlib.pyplot as plt


def parse_line(line):
  items = line.split(':')[-1]
  items = items.strip().split(' ')
  d = {}
  for item in items:
    key, value = item.split('=')
    value = value.replace('ms', '')
    d[key] = int(value)
  return d

def parse_file(filename="./data/ping_trace.txt"):
  lines = []
  with open(filename, "r") as pingfile:
    for _ in range(6):
      pingfile.readline() # skip first line
    for line in pingfile:
      try:
        line = parse_line(line)
        lines.append(line)
      except Exception as ex:
        print(ex)
        break
  df = pd.DataFrame(lines)
  print(df)
  return df

def plot_pings(df):
  plt.plot(df['tSent'] / 1000, df['rtt'])
  plt.xlabel("seconds")
  plt.ylabel("rtt (ms)")
  plt.ylim(bottom=0)
  plt.savefig('graphs/ping.png')

def main():
  df = parse_file()
  plot_pings(df)

if __name__ == "__main__":
    main()