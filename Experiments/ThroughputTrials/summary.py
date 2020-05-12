import pandas as pd

import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt


from pylab import rcParams
rcParams['figure.figsize'] = 10, 8

DATA_DIR = './data/2020-05-09/'

def analyze_summary():
    fname = f"{DATA_DIR}/quantiles.csv"
    df = pd.read_csv(fname, index_col=0).dropna()

    df.boxplot()
    plt.title("Throughput by quartile")
    plt.xlabel("quartile")
    plt.savefig(f"{DATA_DIR}/big_box.png")
    plt.close()

    df.boxplot(by='protocol')
    plt.savefig(f"{DATA_DIR}/box_protocol.png")
    plt.close()

    df.boxplot(column=['mean'], by='protocol')
    plt.savefig(f"{DATA_DIR}/mean_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.75'], by='protocol')
    plt.savefig(f"{DATA_DIR}/75_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.5'], by='protocol')
    plt.savefig(f"{DATA_DIR}/50_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.9'], by='protocol')
    plt.savefig(f"{DATA_DIR}/90_box_protocol.png")
    plt.close()

    df.boxplot(column=['1.0'], by='protocol')
    plt.savefig(f"{DATA_DIR}/100_box_protocol.png")
    plt.close()

    df.boxplot(column=['0.25'], by='protocol')
    plt.savefig(f"{DATA_DIR}/25_box_protocol.png")
    plt.close()

    df.boxplot(by='host')
    plt.savefig(f"{DATA_DIR}/box_machine.png")
    plt.close()

if __name__ == "__main__":
    analyze_summary()
