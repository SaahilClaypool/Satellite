#!/usr/bin/python3
from datetime import date
from trial import Trial
import os


def all_trials_main():
    # roughly 1 day of trails
    machines = [
        "mlcnetA.cs.wpi.edu",
        "mlcnetB.cs.wpi.edu",
        "mlcnetC.cs.wpi.edu",
        "mlcnetD.cs.wpi.edu"
    ]
    protocols = [
        "cubic",
        "bbr",
        "hybla",
        "pcc"
    ]

    dir = 'data/' + date.today().strftime("%Y-%m-%d")
    if not os.path.exists(dir):
        os.makedirs(dir)
    # roughly 24 hours
    for i in range(80):
        for machine, protocol in zip(machines, protocols):
            print(machine, protocol)
            title = f"{dir}/{machine}_{protocol}_{i}"
            trial = Trial(name=title, data="1G", remote=machine)
            trial.remote_tc(cc=protocol)
            trial.start()

#    def __init__(self, name='experiment', dir='.', local='glomma', remote='mlc1.cs.wpi.edu', data=None):


if __name__ == "__main__":
    all_trials_main()
