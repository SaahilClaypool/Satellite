#!/usr/bin/python3
from trial import Trial


def all_trials_main():
    # roughly 1 day of trails
    machines = [
        "mlc1",
        "mlc2",
        "mlc3",
        "mlc4"
    ]

    # roughly 24 hours
    for i in range(72):
        for machine in machines:
            title = f"{machine}_{i}"
            trial = Trial(name=title, data="1G", remote=machine)
            trial.start()

#    def __init__(self, name='experiment', dir='.', local='glomma', remote='mlc1.cs.wpi.edu', data=None):


if __name__ == "__main__":
    all_trials_main()
