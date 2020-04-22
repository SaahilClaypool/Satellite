#!/usr/bin/python3
# Main script to generate a trial
import command as cmd
import time

BDP = 65625000

cmd.MOCK = False

class Tc:
    def __init__(self, cc='cubic', win=BDP, host=""):
        self.cc = cc
        self.win = BDP
        self.host = host

    def cmd(self):
        win, cc = self.win, self.cc
        command = ' && '.join([
            f"sudo sysctl -w net.ipv4.tcp_mem='{win} {win} {win}'",
            f"sudo sysctl -w net.ipv4.tcp_wmem='{win} {win} {win}'",
            f"sudo sysctl -w net.ipv4.tcp_rmem='{win} {win} {win}'",
            f"sudo sysctl -w net.ipv4.tcp_congestion_control='{cc}'"])
        
        return command

    def setup_tc(self):
        cmd.run_command(self.cmd(), host=self.host)

def sleep(seconds=1):
    if cmd.MOCK:
        print(f'would sleep for {seconds}s')
    else:
        time.sleep(seconds)


class Trial:
    def __init__(self, name='experiment', dir='.', local='glomma', remote='mlc1.cs.wpi.edu'):
        self.name = name
        self.dir = dir
        self.cc = 'cubic'
        self.remote = remote
        self._local_tc = Tc()
        self._remote_tc = Tc()

    def local_tc(self, cc='cubic', win=BDP):
        self._local_tc = Tc(cc, win)

    def remote_tc(self, cc='cubic', win=BDP):
        self._remote_tc = Tc(cc, win, self.remote)

    def _setup_tc(self):
        self._local_tc.setup_tc()
        self._remote_tc.setup_tc()


    def _start_udp_ping(self):
        remote_cmd = "~/.local/bin/sUDPingLnx"
        cmd.run_command(remote_cmd, host=self.remote)

        sleep()

        local_cmd = f"cUDPingLnx -h {self.remote}"
        cmd.run_command(local_cmd)

    def _cleanup(self):
        procs = ['tcpdump', 'cUDPingLnx', 'sUDPingLnx', 'iperf3']
        kill_cmd = 'pkill '+ '; pkill '.join(procs) + ';'
        cmd.run_command(kill_cmd).wait()
        cmd.run_command(kill_cmd, host=self.remote).wait()

    def start(self, time=90):
        """
        0. runes tc
        1. starts udp ping
        2. starts iperf server on remote
        3. starts tcpdump
        4. starts iperf client on local 
        5. kills tcpdump 
        6. copies captures locally
        """
        self._start_udp_ping()
        sleep(10)
        self._cleanup()


