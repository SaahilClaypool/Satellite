
import matplotlib
matplotlib.use('AGG')

from datetime import timedelta
import glob
import matplotlib.pyplot as plt
import os
import pandas as pd

from pylab import rcParams
rcParams['figure.figsize'] = 10, 8


def plot_each_day(folder="./data/"):
  for file in glob.glob(f"{folder}/*.txt"):
    df = parse_file(file)
    base = file.split("/")[-1].replace(".txt", "")
    # plot_pings(df, "graphs/" + base + ".png")
    plot_sampled(df, f"graphs/quantiles", base)
    plot_sampled(df, f"graphs/nomax", base, quantiles=[0.25, 0.5, 0.75], names=["lower", "median", "upper"])
    plot_cdf(df, "graphs/cdf", base)

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


# df = pp.parse_file('./data/ping_trace_20_04_04.txt')
# pp.plot_sampled(df, output_dir='.')
def plot_sampled(df, output_dir='./graphs/rolling', title="quantile", quantiles=[0.0, .25, .5, .75, 1.0], names=["min", "lower", "median", "upper", "max"]):
  
  plt.close()
  if not os.path.exists(output_dir):
    os.mkdir(output_dir)

  df = df[df['systemTime'] > pd.Timestamp('2017-01-01T12')]
  df = df.set_index('systemTime').sort_index()
  r = df.rolling('60s')

  frames = [(name, r.quantile(q)) for name, q in zip(names, quantiles)]

  for name, frame in frames:
    plt.scatter(df.index - timedelta(hours=4), frame['rtt'], alpha=0.10, s=2, label=name)

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

def plot_cdf(df, output_dir="./graphs/cdf", title="cdf.png"):
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
