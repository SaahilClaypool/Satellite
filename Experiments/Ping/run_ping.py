#!/usr/bin/python3
from subprocess import Popen
from optparse import OptionParser
import threading
from datetime import date
from time import sleep

def client_ping(host="mlc1.cs.wpi.edu", output_file="ping_trace.txt"):
  with open(output_file, 'w') as outfile:
    proc = Popen(["cUDPingLnx", "-h", host], stdout=outfile)

    return proc

def date_string():
  return date.today().strftime("%y_%m_%d")


def daily():
  """
  Starts a new thread for client ping. At the end of the day, kill the thread and rejoin to it.
  The file will be suffixed with the date in the data directory.
  """
  while(True):
    today = date_string()
    print(f"Starting recording for {date_string()}...")
    output_file = f"data/ping_trace_{date_string()}.txt"
    proc = client_ping(output_file=output_file)

    while(True):
      sleep(60)
      current_date = date_string()
      if (current_date != today): # we have passed into the next tday
        proc.kill()
        break


def main():
  parser = OptionParser()
  parser.add_option("-d", "--daily",
                  action="store_true", dest="daily", default=False,
                  help="Output the data to a new file each day")

if __name__ == "__main__":
  daily()