from datetime import date
from trial import Trial
import os

import analyze as az
import summary as sm


def main():
    dir = 'pcc'
    if not os.path.exists(dir):
        os.makedirs(dir)

    machine = "mlcnetD.cs.wpi.edu"
    protocol = "pcc"

    title = f"{dir}/{machine}_{protocol}"
    trial = Trial(name=title, data="1G", remote=machine)
    trial.remote_tc(cc=protocol)
    dir = trial.data_dir()

    trial.start()
    # az.DATA_DIR = './data/pcc'
    # az.main()

if __name__ == "__main__":
    main()