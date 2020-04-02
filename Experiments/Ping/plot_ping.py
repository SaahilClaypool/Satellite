#!/usr/bin/python3

import matplotlib
matplotlib.use('AGG')

import pandas as pd
import matplotlib.pyplot as plt
import glob


def plot_each_day(folder="./data/"):
  for file in glob.glob(f"{folder}/*.txt"):
    df = parse_file(file)
    plot_pings(df, "graphs/" + file.split("/")[-1].replace(".txt", ".png"))

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
  return df

def plot_pings(df, output_file="./graphs/ping.png"):
  plt.scatter(df['tSent'] / 1000, df['rtt'], alpha=0.05)
  plt.xlabel("seconds")
  plt.ylabel("rtt (ms)")
  plt.ylim(bottom=0)
  plt.savefig(output_file)
  plt.close()

def main():
  plot_each_day()

if __name__ == "__main__":
    main()
