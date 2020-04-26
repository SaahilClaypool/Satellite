#!/usr/bin/python3

from time import time
from os import system

hosts = ["mlc1", "mlc2", "mlc3", "mlc4"]

bad = False

for host in hosts:

  start_time = time()
  system(f"nc -zv {host} 81 1> /dev/null 2> /dev/null")
  end_time = time()

  if end_time - start_time < 0.3: # 300 milliseconds
    print(f"Proxy is on for {host} - ping only took {end_time - start_time} seconds.\n\tTCP looks like its going through proxy")
    print(f"run setup_routes.sh")
  else:
    print(f"things look good to {host} - ping took {end_time - start_time} seconds")

if bad:
  exit(-1)
else:
  exit(0)
