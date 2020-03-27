#!/usr/bin/python3

from time import time
from os import system

start_time = time()
system('nc -zv mlc1 81 1> /dev/null 2> /dev/null')
end_time = time()

if end_time - start_time < 0.3: # 300 milliseconds
  print("Proxy is on - ping only took {end_time - start_time} seconds.\n\tTCP looks like its going through proxy")
  exit(-1)
else:
  print(f"things look good - ping took {end_time - start_time} seconds")
  exit(0)