
import matplotlib
matplotlib.use('AGG')

from datetime import timedelta
import glob
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np

from pylab import rcParams
rcParams['figure.figsize'] = 10, 8


def all_frames(folder="./data/"):
  dataframes = []
  for file in glob.glob(f"{folder}/*.txt"):
    df = parse_file(file)
    dataframes.append(df)

    break # temp

  df = pd.concat(dataframes)

  return df

def plot_all_frame(folder="./data"):
  df = all_frames(folder)
  plot_windowed_loss(df, datefmt="%m/%d", output_dir='./graphs/all/')


def plot_each_day(folder="./data/"):
  for file in glob.glob(f"{folder}/*.txt"):
    df = parse_file(file)
    base = file.split("/")[-1].replace(".txt", "")
    # plot_pings(df, "graphs/" + base + ".png")
    plot_sampled(df, f"graphs/quantiles", base)
    plot_sampled(df, f"graphs/nomax", base, quantiles=[0.25, 0.5, 0.75], names=["lower", "median", "upper"])
    plot_cdf(df, "graphs/cdf", base)
    plot_ccdf(df, "graphs/ccdf", base)

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
  df = pd.DataFrame(lines).dropna()
  df['systemTime'] = df['systemTime'].apply(lambda x: pd.Timestamp(x / 1000, unit='s'))
  return df

def setup(output_dir):
  plt.close()
  if not os.path.exists(output_dir):
    os.mkdir(output_dir)

def resample(df, window='60s'):
  df = df[df['systemTime'] > pd.Timestamp('2017-01-01T12')]
  df = df.set_index('systemTime').sort_index()
  r = df.resample(window)
  return r

def get_i(r, i=0):
  x = 0
  for _ind, ri in r:
    if x == i:
      return ri
    x += 1

def plot_windowed_loss(df, output_dir='./graphs/loss', title='loss', window='60s', datefmt="%H:%M:%S"):
  setup(output_dir)
  lw = windowed_loss(df)
  lw = lw[lw['loss'] < 99]

  # Summary

  windows_with_loss = lw[lw['loss'] > 0]
  percent_minutes = windows_with_loss.count() / lw.count()
  min_str = f"Percent of minutes with loss: {percent_minutes}"
  print(min_str)
  mean_str = f"mean of windows with loss {windows_with_loss.loss.mean()}"
  print(mean_str)

  # Plot

  plt.plot(lw.index - timedelta(hours=4), lw['loss'], label='loss (%)')
  plt.xlabel("time ")
  plt.ylabel("loss percent")
  plt.ylim(bottom=0)
  plt.title(title + ' loss')
  for lh in plt.legend().legendHandles: 
    lh.set_alpha(1)

  plt.text(.5, .5, f"{min_str}\n{mean_str}")
  print("Added labels")
  date_formatter = matplotlib.dates.DateFormatter(datefmt)
  ax=plt.gca()
  ax.xaxis.set_major_formatter(date_formatter)


  fname = f"{output_dir}/{title}_loss.png"
  plt.savefig(fname)
  print(f"saved to {fname}")
  plt.close()


def windowed_loss(df, window='60s'):
  r = resample(df)
  loss_windows = pd.DataFrame(index=['systemTime'])

  for ind, ri in r:
    packets_sent = ri.seq.max() - ri.seq.min() + 1
    packets_received = ri.seq.count()
    loss = 100 - packets_received / packets_sent  * 100
    loss_windows = loss_windows.append([{'systemTime': ind, 'loss': loss}]).dropna()

  loss_windows = loss_windows.set_index('systemTime').sort_index()

  return loss_windows


# df = pp.parse_file('./data/ping_trace_20_04_04.txt')
# pp.plot_sampled(df, output_dir='.')
def plot_sampled(df, output_dir='./graphs/rolling', title="quantile", quantiles=[0.0, .25, .5, .75, 1.0], names=["min", "lower", "median", "upper", "max"], window='60s'):
  
  plt.close()
  if not os.path.exists(output_dir):
    os.mkdir(output_dir)

  r = resample(df)

  frames = [(name, r.quantile(q)) for name, q in zip(names, quantiles)]

  for name, frame in frames:
    plt.scatter(frame.index - timedelta(hours=4), frame['rtt'], alpha=0.50, s=5, label=name)

  # Plot ping graphs
  plt.xlabel("time ")
  plt.ylabel("rtt (ms)")
  plt.ylim(bottom=0)
  plt.title(title)
  for lh in plt.legend().legendHandles: 
    lh.set_alpha(1)

  date_formatter = matplotlib.dates.DateFormatter("%H:%M:%S")
  ax=plt.gca()
  ax.xaxis.set_major_formatter(date_formatter)


  plt.savefig(f"{output_dir}/{title}.png")
  plt.close()

  # Plot loss graphs
  loss_windows = windowed_loss(df)
  plt.plot(loss_windows.index - timedelta(hours=4), loss_windows['loss'], label='loss (%)')
  plt.xlabel("time ")
  plt.ylabel("loss percent")
  plt.ylim(bottom=0)
  plt.title(title + ' loss')
  for lh in plt.legend().legendHandles: 
    lh.set_alpha(1)

  date_formatter = matplotlib.dates.DateFormatter("%H:%M:%S")
  ax=plt.gca()
  ax.xaxis.set_major_formatter(date_formatter)


  plt.savefig(f"{output_dir}/{title}_loss.png")
  plt.close()


def plot_cdf(df, output_dir="./graphs/cdf", title="cdf"):
  plt.close()
  if not os.path.exists(output_dir):
    os.mkdir(output_dir)

  sorted_rtts = df['rtt'].sort_values().reset_index()
  plt.close()
  plt.plot(sorted_rtts.rtt, sorted_rtts.index / sorted_rtts.rtt.count() * 100)
  plt.ylabel("Percent")
  plt.xlabel("ping (ms)")
  plt.title(f"CDF of {title}")
  plt.savefig(f"{output_dir}/{title}.png")

def plot_ccdf(df, output_dir="./graphs/cdf", title="ccdf"):
  plt.close()
  if not os.path.exists(output_dir):
    os.mkdir(output_dir)

  sorted_rtts = df['rtt'].sort_values().reset_index()
  plt.scatter(sorted_rtts.rtt, (1 - sorted_rtts.index / sorted_rtts.rtt.count()) * 100)
  plt.ylabel("Percent")
  plt.xlabel("log (ping (ms))")
  plt.title(f"CDF of {title}")
  plt.xscale('log')
  plt.yscale('log')
  plt.savefig(f"{output_dir}/{title}.png")
  plt.close()
  

def plot_pings(df, output_file="./graphs/ping.png"):
  plt.scatter(df['tSent'] / 1000, df['rtt'], alpha=0.05, s=1)
  plt.xlabel("seconds")
  plt.ylabel("rtt (ms)")
  plt.ylim(bottom=0)
  plt.savefig(output_file)
  plt.close()

def main():
  plot_each_day()

if __name__ == "__main__":
    main()
