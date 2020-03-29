#!/bin/bash
g++ cUDPingLnx.cpp -o cUDPingLnx -lpthread
cp ./cUDPingLnx ~/.local/bin/

g++ sUDPingLnx.cpp -o sUDPingLnx
cp ./sUDPingLnx ~/.local/bin/