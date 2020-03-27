#!/usr/bin/python3
"""
pingpong:

Sends a ping each second.
Generally, we could just look at pcap for the data.
But, this will give us application level data for how long things are taking as a csv
without parsing.
"""

import socket
import sys
from optparse import OptionParser
from time import sleep
import time

def client(options):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  client_address = (socket.gethostname(), options.port)
  print(f'connecting to')
  sock.connect(client_address)
  ping(sock)

def server(options):
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  server_address = (socket.gethostname(), options.port)
  print(f'server listening on {server_address[0]}:{server_address[1]}')
  sock.bind(server_address)

  sock.listen()

  (connection, client_address) = sock.accept()
  print(f'received connection from {client_address}')
  pong(connection)

def send(sock, msg):
  sent = sock.send(msg)
  if(sent == 0):
    print("socket closed on send")
    sock.close()
    exit(-1)
  return sent

def recv(sock):
  msg = sock.recv(1024)
  if (msg == b''):
    print("socket closed on recv")
    sock.close()
    exit(-1)
  return msg.decode()

def pong(connection):
  x = 0
  while True:
    msg = f"{x}"
    start_time = time.time()
    sent = send(connection, str.encode(msg))
    print(f"sent {sent} bytes msg: {msg}")
    recd = recv(connection)
    elapsed = (time.time() - start_time) * 1000
    print(f'recd: {recd} in {elapsed} ms')
    sleep(1)
    x+=1


def ping(sock):
  while True:
    recd = recv(sock)
    send(sock, str.encode(recd))

def main():
  parser = OptionParser()
  parser.add_option("-c", "--client", type="string", action="store", dest="client", help="remote host for client mode", default=None)
  parser.add_option("-p", "--port", type="int", action="store", dest="port", help="port", default=7878)

  (options, args) = parser.parse_args()
  print(options)

  if(options.client):
    client(options)
  else:
    server(options)


if __name__ == "__main__":
  main()