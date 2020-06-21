#!/usr/bin/python3
from datetime import date
from trial import Trial
import os


BDP = 15000000 # .6 * 200 * 125000

def window_sizes():
    dir = 'data/WINDOW_SIZES/' + date.today().strftime("%Y-%m-%d")
    if not os.path.exists(dir):
        os.makedirs(dir)
    # roughly 24 hours
    wmems = [
        int(BDP * 0.5),
        BDP * 1,
        BDP * 2,
        BDP * 4,
        BDP * 8,
        BDP * 16,
        65625000,
    ]
    for wmem in wmems:
        title = f"{dir}/{wmem}"
        trial = Trial(name=title, data="1G", remote='mlc1')
        trial.remote_tc(cc='cubic', win=wmem)
        trial.local_tc(cc='cubic', win=wmem)
        trial.start()

#    def __init__(self, name='experiment', dir='.', local='glomma', remote='mlc1.cs.wpi.edu', data=None):


if __name__ == "__main__":
    window_sizes()
